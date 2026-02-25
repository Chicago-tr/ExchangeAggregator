import {
  pgTable,
  timestamp,
  varchar,
  uuid,
  serial,
  integer,
  unique,
  real,
} from "drizzle-orm/pg-core";

export const prices = pgTable("prices", {
  id: uuid("id").primaryKey().defaultRandom(),
  timeStamp: timestamp("TimeStamp").notNull().defaultNow(),
  bid: real("Bid"),
  ask: real("Ask"),
  exchangeId: integer("ExchangeId").references(() => exchanges.id),
  symbolId: integer("SymbolId").references(() => symbols.id),
});
export type newPrices = typeof prices.$inferInsert;

export const exchanges = pgTable("exchanges", {
  id: serial("id").primaryKey(),
  name: varchar("ExchangeName").unique(),
});
export type exchanges = typeof exchanges.$inferInsert;

export const symbols = pgTable(
  "symbols",
  {
    id: serial("id").primaryKey(),
    baseAsset: varchar("BaseAsset"),
    quoteAsset: varchar("QuoteAsset"),
    symbolCode: varchar("SymbolCode"),
  },
  (t) => ({ unq: unique().on(t.baseAsset, t.quoteAsset, t.symbolCode) }),
);
export type symbols = typeof symbols.$inferInsert;
