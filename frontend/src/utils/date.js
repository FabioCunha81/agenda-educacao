export function formatDateBR(value) {
  if (!value) return "-";
  const [year, month, day] = String(value).split("-");
  if (!year || !month || !day) return value;
  return `${day}/${month}/${year}`;
}

export function formatLocalISODate(date) {
  if (!date) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

export function normalizeTime(value) {
  if (typeof value !== "string") return "";

  const match = value.trim().match(/^(\d{1,2}):(\d{2})(?::\d{2})?(?:\.\d+)?(?:Z)?$/);
  if (!match) return "";

  const hours = Number(match[1]);
  const minutes = Number(match[2]);

  if (
    !Number.isInteger(hours) ||
    !Number.isInteger(minutes) ||
    hours < 0 ||
    hours > 23 ||
    minutes < 0 ||
    minutes > 59
  ) {
    return "";
  }

  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

export function addHoursToTime(value, hoursToAdd) {
  const normalized = normalizeTime(value);
  if (!normalized) return "";

  const [hours, minutes] = normalized.split(":").map(Number);
  const totalMinutes = ((hours * 60) + minutes + (hoursToAdd * 60)) % (24 * 60);

  return `${String(Math.floor(totalMinutes / 60)).padStart(2, "0")}:${String(
    totalMinutes % 60
  ).padStart(2, "0")}`;
}
