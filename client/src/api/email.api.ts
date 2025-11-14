import { SuscribeEmail } from "@/types/models";
import { PROJECT_ENV } from "@/utils/env";

export const suscribeEmail = async (dto: SuscribeEmail): Promise<boolean> => {
  // hora en utc
  dto.hours = new Date().getUTCHours();
  dto.minutes = new Date().getUTCMinutes();

  const data: SuscribeEmail = {
    ...dto,
    hours: dto.hours,
    minutes: dto.minutes,
  };

  const response = await fetch(`${PROJECT_ENV.API_URL}/reports/subscriptions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  return response.ok;
};
