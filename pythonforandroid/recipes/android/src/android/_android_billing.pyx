# -------------------------------------------------------------------
# Billing
cdef extern void android_billing_service_start()
cdef extern void android_billing_service_stop()
cdef extern void android_billing_buy(char *sku)
cdef extern char *android_billing_get_purchased_items()
cdef extern char *android_billing_get_pending_message()

class BillingService(object):

    BILLING_ACTION_SUPPORTED = 'billingsupported'
    BILLING_ACTION_ITEMSCHANGED = 'itemschanged'

    BILLING_TYPE_INAPP = 'inapp'
    BILLING_TYPE_SUBSCRIPTION = 'subs'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.purchased_items = None
        android_billing_service_start()

    def _stop(self):
        android_billing_service_stop()

    def buy(self, sku):
        cdef char *j_sku = <bytes>sku
        android_billing_buy(j_sku)

    def get_purchased_items(self):
        cdef char *items = NULL
        cdef bytes pitem
        items = android_billing_get_purchased_items()
        if items == NULL:
            return []
        pitems = items
        ret = {}
        for item in pitems.split('\n'):
            if not item:
                continue
            sku, qt = item.split(',')
            ret[sku] = {'qt': int(qt)}
        return ret

    def check(self, *largs):
        cdef char *message
        cdef bytes pymessage

        while True:
            message = android_billing_get_pending_message()
            if message == NULL:
                break
            pymessage = <bytes>message
            self._handle_message(pymessage)

        if self.purchased_items is None:
            self._check_new_items()

    def _handle_message(self, message):
        action, data = message.split('|', 1)
        #print "HANDLE MESSAGE-----", (action, data)

        if action == 'billingSupported':
            tp, value = data.split('|')
            value = True if value == '1' else False
            self.callback(BillingService.BILLING_ACTION_SUPPORTED, tp, value)

        elif action == 'requestPurchaseResponse':
            self._check_new_items()

        elif action == 'purchaseStateChange':
            self._check_new_items()

        elif action == 'restoreTransaction':
            self._check_new_items()

    def _check_new_items(self):
        items = self.get_purchased_items()
        if self.purchased_items != items:
            self.purchased_items = items
            self.callback(BillingService.BILLING_ACTION_ITEMSCHANGED, self.purchased_items)
