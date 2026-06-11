import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig(({ mode }) => ({
    plugins: [react(), tailwindcss()],
    build: {
        rollupOptions: {
            output: {
                manualChunks: {
                    vendor: ['react', 'react-dom', 'react-router-dom'],
                    ui: ['antd', '@ant-design/icons'],
                },
            },
        },
        sourcemap: mode !== 'production', // sourcemap только в dev
        minify: 'terser',
        terserOptions: {
            compress: { drop_console: true, drop_debugger: true },
        },
    },
}));