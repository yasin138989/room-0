export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        midnight: '#070b16',
        panel: '#111827',
        neon: '#5eead4',
        gold: '#d4af37',
        danger: '#ef4444'
      },
      boxShadow: {
        glow: '0 0 30px rgba(94,234,212,0.25)'
      }
    }
  },
  plugins: []
};
