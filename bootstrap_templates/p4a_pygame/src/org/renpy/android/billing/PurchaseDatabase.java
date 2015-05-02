/*
 * Copyright (C) 2010 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.renpy.android.billing;

import org.renpy.android.billing.Consts.PurchaseState;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.util.Log;

/**
 * An example database that records the state of each purchase. You should use
 * an obfuscator before storing any information to persistent storage. The
 * obfuscator should use a key that is specific to the device and/or user.
 * Otherwise an attacker could copy a database full of valid purchases and
 * distribute it to others.
 */
public class PurchaseDatabase {
    private static final String TAG = "PurchaseDatabase";
    private static final String DATABASE_NAME = "purchase.db";
    private static final int DATABASE_VERSION = 1;
    private static final String PURCHASE_HISTORY_TABLE_NAME = "history";
    private static final String PURCHASED_ITEMS_TABLE_NAME = "purchased";

    // These are the column names for the purchase history table. We need a
    // column named "_id" if we want to use a CursorAdapter. The primary key is
    // the orderId so that we can be robust against getting multiple messages
    // from the server for the same purchase.
    static final String HISTORY_ORDER_ID_COL = "_id";
    static final String HISTORY_STATE_COL = "state";
    static final String HISTORY_PRODUCT_ID_COL = "productId";
    static final String HISTORY_PURCHASE_TIME_COL = "purchaseTime";
    static final String HISTORY_DEVELOPER_PAYLOAD_COL = "developerPayload";

    private static final String[] HISTORY_COLUMNS = {
        HISTORY_ORDER_ID_COL, HISTORY_PRODUCT_ID_COL, HISTORY_STATE_COL,
        HISTORY_PURCHASE_TIME_COL, HISTORY_DEVELOPER_PAYLOAD_COL
    };

    // These are the column names for the "purchased items" table.
    static public final String PURCHASED_PRODUCT_ID_COL = "_id";
    static public final String PURCHASED_QUANTITY_COL = "quantity";

    private static final String[] PURCHASED_COLUMNS = {
        PURCHASED_PRODUCT_ID_COL, PURCHASED_QUANTITY_COL
    };

    private SQLiteDatabase mDb;
    private DatabaseHelper mDatabaseHelper;

    public PurchaseDatabase(Context context) {
        mDatabaseHelper = new DatabaseHelper(context);
        mDb = mDatabaseHelper.getWritableDatabase();
    }

    public void close() {
        mDatabaseHelper.close();
    }

    /**
     * Inserts a purchased product into the database. There may be multiple
     * rows in the table for the same product if it was purchased multiple times
     * or if it was refunded.
     * @param orderId the order ID (matches the value in the product list)
     * @param productId the product ID (sku)
     * @param state the state of the purchase
     * @param purchaseTime the purchase time (in milliseconds since the epoch)
     * @param developerPayload the developer provided "payload" associated with
     *     the order.
     */
    private void insertOrder(String orderId, String productId, PurchaseState state,
            long purchaseTime, String developerPayload) {
        ContentValues values = new ContentValues();
        values.put(HISTORY_ORDER_ID_COL, orderId);
        values.put(HISTORY_PRODUCT_ID_COL, productId);
        values.put(HISTORY_STATE_COL, state.ordinal());
        values.put(HISTORY_PURCHASE_TIME_COL, purchaseTime);
        values.put(HISTORY_DEVELOPER_PAYLOAD_COL, developerPayload);
        mDb.replace(PURCHASE_HISTORY_TABLE_NAME, null /* nullColumnHack */, values);
    }

    /**
     * Updates the quantity of the given product to the given value. If the
     * given value is zero, then the product is removed from the table.
     * @param productId the product to update
     * @param quantity the number of times the product has been purchased
     */
    private void updatePurchasedItem(String productId, int quantity) {
        if (quantity == 0) {
            mDb.delete(PURCHASED_ITEMS_TABLE_NAME, PURCHASED_PRODUCT_ID_COL + "=?",
                    new String[] { productId });
            return;
        }
        ContentValues values = new ContentValues();
        values.put(PURCHASED_PRODUCT_ID_COL, productId);
        values.put(PURCHASED_QUANTITY_COL, quantity);
        mDb.replace(PURCHASED_ITEMS_TABLE_NAME, null /* nullColumnHack */, values);
    }

    /**
     * Adds the given purchase information to the database and returns the total
     * number of times that the given product has been purchased.
     * @param orderId a string identifying the order
     * @param productId the product ID (sku)
     * @param purchaseState the purchase state of the product
     * @param purchaseTime the time the product was purchased, in milliseconds
     * since the epoch (Jan 1, 1970)
     * @param developerPayload the developer provided "payload" associated with
     *     the order
     * @return the number of times the given product has been purchased.
     */
    public synchronized int updatePurchase(String orderId, String productId,
            PurchaseState purchaseState, long purchaseTime, String developerPayload) {
        insertOrder(orderId, productId, purchaseState, purchaseTime, developerPayload);
        Cursor cursor = mDb.query(PURCHASE_HISTORY_TABLE_NAME, HISTORY_COLUMNS,
                HISTORY_PRODUCT_ID_COL + "=?", new String[] { productId }, null, null, null, null);
        if (cursor == null) {
            return 0;
        }
        int quantity = 0;
        try {
            // Count the number of times the product was purchased
            while (cursor.moveToNext()) {
                int stateIndex = cursor.getInt(2);
                PurchaseState state = PurchaseState.valueOf(stateIndex);
                // Note that a refunded purchase is treated as a purchase. Such
                // a friendly refund policy is nice for the user.
                if (state == PurchaseState.PURCHASED || state == PurchaseState.REFUNDED) {
                    quantity += 1;
                }
            }

            // Update the "purchased items" table
            updatePurchasedItem(productId, quantity);
        } finally {
            if (cursor != null) {
                cursor.close();
            }
        }
        return quantity;
    }

    /**
     * Returns a cursor that can be used to read all the rows and columns of
     * the "purchased items" table.
     */
    public Cursor queryAllPurchasedItems() {
        return mDb.query(PURCHASED_ITEMS_TABLE_NAME, PURCHASED_COLUMNS, null,
                null, null, null, null);
    }

    /**
     * This is a standard helper class for constructing the database.
     */
    private class DatabaseHelper extends SQLiteOpenHelper {
        public DatabaseHelper(Context context) {
            super(context, DATABASE_NAME, null, DATABASE_VERSION);
        }

        @Override
        public void onCreate(SQLiteDatabase db) {
            createPurchaseTable(db);
        }

        @Override
        public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
            // Production-quality upgrade code should modify the tables when
            // the database version changes instead of dropping the tables and
            // re-creating them.
            if (newVersion != DATABASE_VERSION) {
                Log.w(TAG, "Database upgrade from old: " + oldVersion + " to: " +
                    newVersion);
                db.execSQL("DROP TABLE IF EXISTS " + PURCHASE_HISTORY_TABLE_NAME);
                db.execSQL("DROP TABLE IF EXISTS " + PURCHASED_ITEMS_TABLE_NAME);
                createPurchaseTable(db);
                return;
            }
        }

        private void createPurchaseTable(SQLiteDatabase db) {
            db.execSQL("CREATE TABLE " + PURCHASE_HISTORY_TABLE_NAME + "(" +
                    HISTORY_ORDER_ID_COL + " TEXT PRIMARY KEY, " +
                    HISTORY_STATE_COL + " INTEGER, " +
                    HISTORY_PRODUCT_ID_COL + " TEXT, " +
                    HISTORY_DEVELOPER_PAYLOAD_COL + " TEXT, " +
                    HISTORY_PURCHASE_TIME_COL + " INTEGER)");
            db.execSQL("CREATE TABLE " + PURCHASED_ITEMS_TABLE_NAME + "(" +
                    PURCHASED_PRODUCT_ID_COL + " TEXT PRIMARY KEY, " +
                    PURCHASED_QUANTITY_COL + " INTEGER)");
        }
    }
}
