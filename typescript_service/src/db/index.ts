import { drizzle, PostgresJsDatabase } from "drizzle-orm/postgres-js";
import postgres from "postgres";

import * as schema from "./schema.js";
import { config } from "../config.js";
import { exchanges, symbols } from "./schema.js";

const con = postgres(config.db.url);
export const db = drizzle(con, { schema });
