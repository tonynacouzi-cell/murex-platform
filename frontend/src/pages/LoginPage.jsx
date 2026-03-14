@import url('https://rsms.me/inter/inter.css');
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html { font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11'; }
  body {
    font-family: 'Inter var', Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
}

@layer utilities {
  .shadow-elevated {
    box-shadow: 0 10px 40px -10px rgba(30, 58, 95, 0.15), 0 2px 8px -2px rgba(0,0,0,0.05);
  }
  .shadow-card {
    box-shadow: 0 1px 3px 0 rgba(0,0,0,0.06), 0 1px 2px -1px rgba(0,0,0,0.06);
  }
  .shadow-card-hover {
    box-shadow: 0 4px 12px 0 rgba(0,0,0,0.08), 0 2px 4px -1px rgba(0,0,0,0.06);
  }
}
