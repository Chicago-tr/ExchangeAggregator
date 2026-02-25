import { MigrationConfig } from "drizzle-orm/migrator";
import { envOrThrow } from "./helpers.js";

process.loadEnvFile();

type Config = {
  db: DBConfig;
};

type DBConfig = { url: string; migrationConfig: MigrationConfig };

const migrationConfig: MigrationConfig = {
  migrationsFolder: "./src/db/migrations",
};

export const config: Config = {
  db: {
    url: envOrThrow("DB_URL"),
    migrationConfig: migrationConfig,
  },
};
