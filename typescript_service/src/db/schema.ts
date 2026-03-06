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
  timestamp: timestamp("timestamp").notNull().defaultNow(),
  bid: real("bid"),
  ask: real("ask"),
  exchange_id: integer("exchange_id").references(() => exchanges.id),
  symbol_id: integer("symbol_id").references(() => symbols.id),
});
export type newPrices = typeof prices.$inferInsert;

export const exchanges = pgTable("exchanges", {
  id: serial("id").primaryKey(),
  exchange_name: varchar("exchange_name").unique(),
});
export type exchanges = typeof exchanges.$inferInsert;

export const symbols = pgTable(
  "symbols",
  {
    id: serial("id").primaryKey(),
    base_asset: varchar("base_asset"),
    quote_asset: varchar("quote_asset"),
    symbol_code: varchar("symbol_code"),
  },
  (t) => ({ unq: unique().on(t.base_asset, t.quote_asset, t.symbol_code) }),
);
export type symbols = typeof symbols.$inferInsert;

export const etl_state = pgTable("etl_state", {
  id: varchar("id").primaryKey(),
  last_processed: timestamp("last_processed").notNull().defaultNow(),
});
