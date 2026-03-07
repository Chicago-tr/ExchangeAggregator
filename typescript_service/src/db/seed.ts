import { db } from "./index.js";
import { etl_state, exchanges, symbols } from "./schema.js";

export async function seedTables() {
  const exchangeList = [
    { exchange_name: "Binance" },
    { exchange_name: "Coinbase" },
  ];
  await db
    .insert(exchanges)
    .values(exchangeList)
    .onConflictDoNothing({ target: exchanges.exchange_name });

  /*
  const coinbase = {
    baseAsset: "BTC",
    quoteAsset: "USD",
    symbolCode: "BTC-USD",
  };
  */
  const btcusd = {
    base_asset: "BTC",
    quote_asset: "USD",
    symbol_code: "BTC-USD",
  };
  const ethusd = {
    base_asset: "ETH",
    quote_asset: "USD",
    symbol_code: "ETH-USD",
  };
  const solusd = {
    base_asset: "SOL",
    quote_asset: "USD",
    symbol_code: "SOL-USD",
  };

  //await db.insert(symbols).values(coinbase).onConflictDoNothing();
  await db.insert(symbols).values(btcusd).onConflictDoNothing();
  await db.insert(symbols).values(ethusd).onConflictDoNothing();
  await db.insert(symbols).values(solusd).onConflictDoNothing();

  //default date just set to distant past so we use all collected data initially
  const date = new Date(0);
  const stateData = { id: "bars_and_cross_spread_1m", last_processed: date };
  await db
    .insert(etl_state)
    .values(stateData)
    .onConflictDoNothing({ target: etl_state.id });
}
