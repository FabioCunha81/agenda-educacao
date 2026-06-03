const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export function getToken() {
  return localStorage.getItem("accessToken");
}

function formatApiError(data) {
  if (!data || data instanceof Blob) {
    return "Não foi possível concluir a operação.";
  }
  if (data.detail) {
    return data.detail;
  }
  if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
    return data.non_field_errors[0];
  }
  if (typeof data === "object") {
    const fieldMessages = Object.entries(data)
      .map(([field, value]) => {
        if (Array.isArray(value)) {
          return `${field}: ${value.join(" ")}`;
        }
        if (typeof value === "string") {
          return `${field}: ${value}`;
        }
        return null;
      })
      .filter(Boolean);
    if (fieldMessages.length) {
      return fieldMessages.join(" ");
    }
  }
  return "Não foi possível concluir a operação.";
}

export async function api(path, options = {}) {
  const { redirectOnUnauthorized = true, ...fetchOptions } = options;
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const token = getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...fetchOptions, headers });
  } catch {
    throw new Error("Não foi possível conectar à API. Verifique se o deploy da API terminou e se o serviço agenda-educacao-api está online.");
  }
  if (response.status === 204) {
    return null;
  }
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : await response.blob();
  if (!response.ok) {
    if (response.status === 401 && redirectOnUnauthorized) {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    throw new Error(formatApiError(data));
  }
  return data;
}

export function downloadUrl(path) {
  return `${API_URL}${path}`;
}
