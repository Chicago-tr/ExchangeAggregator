import { CoinbaseApi, BinanceApi } from "./api.js";
import { envOrThrow, sleep } from "./helpers.js";
import { config } from "./config.js";
import postgres from "postgres";
import { drizzle } from "drizzle-orm/postgres-js/driver";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import { seedTables } from "./db/seed.js";
import {
  insertBinancePrice,
  insertCoinbasePrice,
} from "./db/queries/prices.js";
import { logLatency } from "./db/queries/latencies.js";
async function main() {
  process.loadEnvFile();

  const migrationClient = postgres(config.db.url, { max: 1 });

  await migrate(drizzle(migrationClient), config.db.migrationConfig);
  //Seeds exchange and symbol data into respective tables if it's not there
  await seedTables();

  const pairs = envOrThrow("PAIRS");
  const pairsSplit = pairs.split(",");

  const CoinBaseApi = new CoinbaseApi();
  const BinApi = new BinanceApi();

  while (true) {
    for (const sym of pairsSplit) {
      await insertBinancePrice(sym);
      await insertCoinbasePrice(sym);
    }
    await sleep(2000); //interval to run http requests on (in ms)- check exchange limits
  }
}
main();
