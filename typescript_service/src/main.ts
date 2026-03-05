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

  const CoinPairs = envOrThrow("COINBASE_PAIRS");
  const BinPairs = envOrThrow("BINANCE_PAIRS");

  const CoinBaseApi = new CoinbaseApi();
  const BinApi = new BinanceApi();

  while (true) {
    await insertBinancePrice("BTC-USD");
    await insertCoinbasePrice("BTC-USD");

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
