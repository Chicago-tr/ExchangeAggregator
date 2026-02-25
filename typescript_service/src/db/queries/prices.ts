import { BinanceApi, CoinbaseApi } from "../../api.js";
import { db } from "../index.js";
import { exchanges, newPrices, prices, symbols } from "../schema.js";

/* Old
export async function createPrice(CoinPrice: string, BinPrice: string) {
  const [result] = await db
    .insert(prices)
    .values({ CoinPrice: CoinPrice, BinancePrice: BinPrice })
    .returning();
  return result ?? null;
}
*/

const exchangeNameToId = new Map<string, number>();
const symbolCodeToId = new Map<string, number>();

async function loadReferenceData() {
  //This function queries the database tables and inserts a name/symbol-id pair into constant variables
  //The variables are used to get the table id of an exchange name or symbol when creating a price entry
  //Data for the exchange and symbol tables is currently hardcoded since it's just names
  const exchangeData = await db
    .select({ id: exchanges.id, name: exchanges.name })
    .from(exchanges);
  for (let row of exchangeData) {
    if (row.name) {
      exchangeNameToId.set(row.name, row.id);
    } else {
      throw new Error("Failed to load an exchange name for reference.");
    }
  }

  const symbolsData = await db
    .select({ id: symbols.id, symbolCode: symbols.symbolCode })
    .from(symbols);
  for (let row of symbolsData) {
    if (row.symbolCode) {
      symbolCodeToId.set(row.symbolCode, row.id);
    } else {
      throw new Error("Failed to load a symbol code for reference.");
    }
  }
}

export async function createPriceEntry(
  exchangeName: string,
  symbol: string,
  price: number,
) {
  await loadReferenceData();
  const exchangeId = exchangeNameToId.get(exchangeName);
  const symbolId = symbolCodeToId.get(symbol);

  if (exchangeId == null || symbolId == null) {
    throw new Error("Unknown exchange or symbol");
  }
  await db
    .insert(prices)
    .values({ exchangeId: exchangeId, symbolId: symbolId, price: price });
}

const CoinApi = new CoinbaseApi();
const BinApi = new BinanceApi();

export async function insertBinancePrice(symbol: string) {
  const data = await BinApi.fetchPrice(symbol);
  await createPriceEntry("Binance", symbol, data);
}

export async function insertCoinbasePrice(symbol: string) {
  const data = await CoinApi.fetchPrice(symbol);
  await createPriceEntry("Coinbase", symbol, data);
}
