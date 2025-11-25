// KIFZL DEV BOT - Configuration File
// by @KIFZLDEV

module.exports = {
  // Bot Information
  bot: {
    name: "KIFZL DEV BOT",
    creator: "@KIFZLDEV",
    version: "1.0.0",
    description: "Telegram Bot untuk Contact Management dan File Conversion"
  },

  // Telegram Bot Token (dari environment variable)
  telegram: {
    token: process.env.TELEGRAM_BOT_TOKEN,
    pollTimeout: 30
  },

  // Owner Configuration
  owner: {
    id: 8317563450,
    username: "@KIFZLDEV"
  },

  // VIP Groups untuk Auto-Verification
  vipGroups: {
    groups: [
      "https://t.me/agentviber12",
      "https://t.me/channelviber"
    ],
    vipDuration: 7 // hari
  },

  // User Roles & Access Levels
  roles: {
    FREE: {
      level: 0,
      name: "FREE",
      features: ["check_count", "check_names", "view_status"]
    },
    VIP: {
      level: 1,
      name: "VIP",
      features: ["all_conversions", "file_operations", "split_merge", "create_contacts"]
    },
    PREMIUM: {
      level: 2,
      name: "PREMIUM",
      features: ["all_vip_features", "extended_duration"]
    },
    OWNER: {
      level: 3,
      name: "OWNER",
      features: ["user_management", "redeem_generation", "statistics"]
    }
  },

  // Supported File Formats
  fileFormats: {
    text: [".txt"],
    vcf: [".vcf"],
    excel: [".xlsx", ".xls"],
    message: [".msg"]
  },

  // Premium Packages
  premiumPackages: {
    PREM_DAY: {
      name: "1 Hari",
      duration: "24 Jam",
      days: 1,
      price: 5000
    },
    PREM_WEEK: {
      name: "7 Hari",
      duration: "Mingguan",
      days: 7,
      price: 25000
    },
    PREM_MONTH: {
      name: "30 Hari",
      duration: "Bulanan",
      days: 30,
      price: 75000
    }
  },

  // Redeem Code Configuration
  redeemCode: {
    codeLength: 12,
    characterSet: "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
  },

  // Session Configuration
  session: {
    timeout: 300, // detik
    autoCleanup: true
  },

  // Data Storage
  storage: {
    usersFile: "users.json",
    redeemFile: "redeem.json",
    sessionsFile: "sessions.json",
    adminsFile: "admins.json"
  },

  // Keyboard Buttons
  buttons: {
    mainMenu: [
      ["🜲 STATUS 🜲"],
      ["🜲 MSG TO TXT 🜲", "🜲 TXT TO VCF 🜲"],
      ["🜲 VCF TO TXT 🜲", "🜲 XLS TO VCF 🜲"],
      ["🜲 CREATE ADM/NAVY 🜲"],
      ["🜲 RAPIKAN TXT 🜲", "🜲 GABUNG FILE 🜲"],
      ["🜲 HITUNG KONTAK 🜲", "🜲 CEK NAMA 🜲"],
      ["🜲 SPLIT FILE 🜲", "🎁 REDEEM CODE 🎁"]
    ],
    cancel: "❌ BATAL ❌"
  },

  // Anti-Theft Protection
  protection: {
    enabled: true,
    creatorName: "(BY @KIFZLDEV)",
    verifyOnStartup: true
  },

  // Messages & Responses
  messages: {
    start: "Selamat datang di KIFZL DEV BOT!",
    welcome: "Pilih menu yang tersedia di bawah ini",
    cancelled: "❌ Proses dibatalkan"
  }
};
