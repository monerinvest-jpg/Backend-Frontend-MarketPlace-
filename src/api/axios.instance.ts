// ✅ frontend/src/api/axios.instance.ts
// Безопасный Axios с автоматическим refresh токенов

import axios, { AxiosError } from 'axios';

// ✅ Access token в памяти (не в localStorage!)
let accessToken: string | null = null;

export const tokenService = {
    getToken: () => accessToken,
    setToken: (token: string) => { accessToken = token; },
    clear: () => { accessToken = null; },
};

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true,  // ✅ Отправляет HttpOnly cookie с refresh token
    timeout: 10000,
});

// Запрос interceptor — добавляем access token
api.interceptors.request.use((config) => {
    const token = tokenService.getToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Флаг для предотвращения множественных refresh запросов
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (err: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) prom.reject(error);
        else prom.resolve(token!);
    });
    failedQueue = [];
};

// Ответ interceptor — обрабатываем 401 и обновляем токены
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as any;

        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then((token) => {
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                    return api(originalRequest);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                // ✅ Refresh token приходит из HttpOnly cookie автоматически
                const { data } = await axios.post(
                    `${import.meta.env.VITE_API_URL}/auth/refresh`,
                    {},
                    { withCredentials: true }
                );

                tokenService.setToken(data.accessToken);
                processQueue(null, data.accessToken);
                originalRequest.headers.Authorization = `Bearer ${data.accessToken}`;
                return api(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError, null);
                tokenService.clear();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);

export default api;