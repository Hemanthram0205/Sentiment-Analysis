require('dotenv').config();

// ✅ Validate required environment variables on startup
const requiredEnv = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'JWT_SECRET', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'];
const missingEnv = requiredEnv.filter(key => !process.env[key]);
if (missingEnv.length > 0) {
  console.error(`❌ Missing required environment variables: ${missingEnv.join(', ')}`);
  process.exit(1);
}

const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const path = require('path');

const app = express();

// ✅ Security Headers
app.use(helmet({ contentSecurityPolicy: false }));

// ✅ Restrict CORS to known origins
const allowedOrigins = [
  'http://localhost:3000',
  'http://127.0.0.1:3000',
  'http://localhost:5500',
  'http://127.0.0.1:5500'
];
app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('CORS policy: origin not allowed'));
    }
  },
  credentials: true
}));

app.use(express.json());
app.use(express.static(path.join(__dirname)));
app.use(passport.initialize());

// ✅ Rate Limiting — Auth routes only
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10,
  message: { error: 'Too many attempts. Please try again in 15 minutes.' },
  standardHeaders: true,
  legacyHeaders: false
});

// ✅ MySQL Connection Pool
const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// ✅ Initialize Database Tables
async function initializeDatabase() {
  try {
    // Users table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255),
        google_id VARCHAR(255) UNIQUE,
        login_attempts INT DEFAULT 0,
        locked_until DATETIME NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Analysis history table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS analyses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        filename VARCHAR(512),
        score FLOAT,
        sentiment VARCHAR(50),
        negative_words TEXT,
        analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
    `);

    console.log('✅ Database initialized.');
  } catch (err) {
    console.error('❌ Failed to initialize database:', err.message);
    process.exit(1);
  }
}
initializeDatabase();

const JWT_SECRET = process.env.JWT_SECRET;

// ✅ Google OAuth Strategy
passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: '/auth/google/callback'
  },
  async (accessToken, refreshToken, profile, done) => {
    try {
      const [existingUser] = await pool.query(
        'SELECT * FROM users WHERE google_id = ?',
        [profile.id]
      );
      if (existingUser.length > 0) return done(null, existingUser[0]);

      const [emailUser] = await pool.query(
        'SELECT * FROM users WHERE email = ?',
        [profile.emails[0].value]
      );
      if (emailUser.length > 0) {
        await pool.query('UPDATE users SET google_id = ? WHERE id = ?', [profile.id, emailUser[0].id]);
        return done(null, emailUser[0]);
      }

      const [newUser] = await pool.query(
        'INSERT INTO users (full_name, email, google_id) VALUES (?, ?, ?)',
        [profile.displayName, profile.emails[0].value, profile.id]
      );
      return done(null, {
        id: newUser.insertId,
        full_name: profile.displayName,
        email: profile.emails[0].value,
        google_id: profile.id
      });
    } catch (err) {
      return done(err, null);
    }
  }
));

// ✅ Google OAuth Routes
app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

app.get('/auth/google/callback',
  passport.authenticate('google', { session: false, failureRedirect: '/login.html?error=google_failed' }),
  (req, res) => {
    const token = jwt.sign(
      { userId: req.user.id, email: req.user.email },
      JWT_SECRET,
      { expiresIn: '1h' }
    );
    // ✅ Set token as HttpOnly cookie instead of exposing in URL
    res.cookie('auth_token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 3600000,
      sameSite: 'lax'
    });
    res.redirect('/login-success.html');
  }
);

// ✅ Register Route
app.post('/api/register', authLimiter, async (req, res) => {
  try {
    const { full_name, email, password } = req.body;
    if (!full_name || !email || !password) {
      return res.status(400).json({ error: 'All fields are required.' });
    }
    if (password.length < 8) {
      return res.status(400).json({ error: 'Password must be at least 8 characters.' });
    }

    const [existingUser] = await pool.query('SELECT id FROM users WHERE email = ?', [email]);
    if (existingUser.length > 0) {
      return res.status(400).json({ error: 'Email already registered.' });
    }

    const hashedPassword = await bcrypt.hash(password, 12);
    const [result] = await pool.query(
      'INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)',
      [full_name, email, hashedPassword]
    );

    const token = jwt.sign({ userId: result.insertId, email }, JWT_SECRET, { expiresIn: '1h' });
    res.status(201).json({ token, user: { id: result.insertId, full_name, email } });
  } catch (err) {
    console.error('Register error:', err.message);
    res.status(500).json({ error: 'Server error.' });
  }
});

// ✅ Login Route with server-side brute-force protection
app.post('/api/login', authLimiter, async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required.' });
    }

    const [users] = await pool.query('SELECT * FROM users WHERE email = ?', [email]);
    if (users.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }

    const user = users[0];

    // ✅ Check lockout
    if (user.locked_until && new Date() < new Date(user.locked_until)) {
      return res.status(429).json({ error: 'Account temporarily locked. Try again later.' });
    }

    if (!user.password) {
      return res.status(401).json({ error: 'This account uses Google login. Please sign in with Google.' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      const newAttempts = (user.login_attempts || 0) + 1;
      if (newAttempts >= 5) {
        const lockUntil = new Date(Date.now() + 15 * 60 * 1000); // Lock for 15 min
        await pool.query('UPDATE users SET login_attempts = ?, locked_until = ? WHERE id = ?', [newAttempts, lockUntil, user.id]);
        return res.status(429).json({ error: 'Too many failed attempts. Account locked for 15 minutes.' });
      }
      await pool.query('UPDATE users SET login_attempts = ? WHERE id = ?', [newAttempts, user.id]);
      return res.status(401).json({ error: 'Invalid credentials.', attemptsLeft: 5 - newAttempts });
    }

    // ✅ Successful login — reset attempts
    await pool.query('UPDATE users SET login_attempts = 0, locked_until = NULL WHERE id = ?', [user.id]);

    const token = jwt.sign({ userId: user.id, email: user.email }, JWT_SECRET, { expiresIn: '1h' });
    res.json({ token, user: { id: user.id, full_name: user.full_name, email: user.email } });
  } catch (err) {
    console.error('Login error:', err.message);
    res.status(500).json({ error: 'Server error.' });
  }
});

// ✅ Get Profile
app.get('/api/profile', authenticateToken, async (req, res) => {
  try {
    const [users] = await pool.query('SELECT id, full_name, email FROM users WHERE id = ?', [req.user.userId]);
    if (users.length === 0) return res.status(404).json({ error: 'User not found.' });
    res.json(users[0]);
  } catch (err) {
    console.error('Profile error:', err.message);
    res.status(500).json({ error: 'Server error.' });
  }
});

// ✅ Save Analysis to DB
app.post('/api/analyses', authenticateToken, async (req, res) => {
  try {
    const { filename, score, sentiment, negative_words } = req.body;
    if (!filename || score === undefined || !sentiment) {
      return res.status(400).json({ error: 'Missing required fields.' });
    }
    await pool.query(
      'INSERT INTO analyses (user_id, filename, score, sentiment, negative_words) VALUES (?, ?, ?, ?, ?)',
      [req.user.userId, filename, score, sentiment, JSON.stringify(negative_words || [])]
    );
    res.status(201).json({ message: 'Analysis saved.' });
  } catch (err) {
    console.error('Save analysis error:', err.message);
    res.status(500).json({ error: 'Server error.' });
  }
});

// ✅ Get User Analysis History from DB
app.get('/api/analyses', authenticateToken, async (req, res) => {
  try {
    const [rows] = await pool.query(
      'SELECT * FROM analyses WHERE user_id = ? ORDER BY analyzed_at DESC LIMIT 50',
      [req.user.userId]
    );
    const analyses = rows.map(r => ({
      ...r,
      negative_words: JSON.parse(r.negative_words || '[]')
    }));
    res.json(analyses);
  } catch (err) {
    console.error('Get analyses error:', err.message);
    res.status(500).json({ error: 'Server error.' });
  }
});

// ✅ JWT Middleware
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.sendStatus(401);
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
});
