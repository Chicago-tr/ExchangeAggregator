export function envOrThrow(key: string) {
  const value = process.env[key];
  if (!value) {
    throw new Error(`no ${key} in env`);
  } else return value;
}

export async function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
