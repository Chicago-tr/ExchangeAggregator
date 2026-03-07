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

async function main() {
  process.loadEnvFile();

  const migrationClient = postgres(config.db.url, { max: 1 });

  await migrate(drizzle(migrationClient), config.db.migrationConfig);

  await seedTables(); //Seeds exchange and symbol data into respective tables if it's not there

  const pairs = envOrThrow("PAIRS");
  const pairsSplit = pairs.split(",");

  const CoinBaseApi = new CoinbaseApi();
  const BinApi = new BinanceApi();
  console.log(pairsSplit);
  while (true) {
    for (const sym of pairsSplit) {
      await insertBinancePrice(sym);
      await insertCoinbasePrice(sym);
    }
    await sleep(2000);
  }
  /*
    console.log(`Coinbase: ${CoinData}`);
    console.log(`Binance: ${BinData}`);
  */
  /*
    const CoinData = await CoinBaseApi.fetchPrice(CoinPairs);
    const BinData = await BinApi.fetchPrice(BinPairs);
    const dat = { CoinPrice: CoinData, BinancePrice: BinData };
    createPrices(CoinData, BinData);
    */
}
main();
