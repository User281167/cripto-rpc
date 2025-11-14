import { SuscribeEmail } from "@/types/models";
import { PROJECT_ENV } from "@/utils/env";

export const suscribeEmail = async (dto: SuscribeEmail): Promise<boolean> => {
  // hora en utc
  const offsetMinutes = new Date().getTimezoneOffset();
  const totalUtcMinutes = dto.hour * 60 + dto.minute + offsetMinutes;

  const utcHour = Math.floor(totalUtcMinutes / 60) % 24;
  const utcMinute = totalUtcMinutes % 60;

  const data: SuscribeEmail = {
    ...dto,
    hour: utcHour,
    minute: utcMinute,
  };

  const response = await fetch(`${PROJECT_ENV.API_URL}/subscriptions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  return response.ok;
};
