// ✅ БЕЗОПАСНО — только для тестов
// src/test/fixtures/users.ts (не импортируется в production-код)
export const mockUsers: User[] = [...];

// vite.config.ts — исключаем из production-бандла
// или используем import.meta.env.DEV guard:
if (import.meta.env.DEV) {
    // загружаем mock-данные только в dev-режиме
}