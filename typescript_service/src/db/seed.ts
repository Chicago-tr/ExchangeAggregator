import { db } from "./index.js";
import { exchanges, symbols } from "./schema.js";

export async function seedTables() {
  const exchangeList = [{ name: "Binance" }, { name: "Coinbase" }];
  await db
    .insert(exchanges)
    .values(exchangeList)
    .onConflictDoNothing({ target: exchanges.name });

  const coinbase = {
    baseAsset: "BTC",
    quoteAsset: "USD",
    symbolCode: "BTC-USD",
  };
  const binance = { baseAsset: "BTC", quoteAsset: "USD", symbolCode: "BTCUSD" };

  await db.insert(symbols).values(coinbase).onConflictDoNothing();
  await db.insert(symbols).values(binance).onConflictDoNothing();
}
