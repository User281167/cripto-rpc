export const PROJECT_ENV: Record<string, string> = {
  API_URL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  SOCKET_URL: import.meta.env.VITE_SOCKET_URL || "http://localhost:8001",
};
