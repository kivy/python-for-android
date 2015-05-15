Manipulating the Android Manifest
---------------------------------

AndroidManifest.xml is built from a template file in python-for-android
distribution. The template is rendered using data from various command
line options to build.py, but some times it is neccessary to add or
change things that there are no options for. To do this, you can provide
python file(s) with your own XML transformations.

The python file must contain a function name `androidmanifest_hook`:

.. code-block:: python
    # root is an xml.etree root node, namespace is an internal identifier
    # for the 'android' xml namespace.
    def androidmanifest_hook(root, namespace):
        pass

You must include the namespace identifier when you manipulate
attributes in the android namespace:

.. code-block:: python
    # Change <manifest android:installLocation=...>
    def androidmanifest_hook(root, namespace):
        root.attrib[namespace + 'installLocation'] = "new value"

.. code-block:: python
    # Find all <service> nodes in <application>
    def androidmanifest_hook(root, namespace):
        elms = root.findall("application/service")
        for service in elms:
            print(service.attrib[namespace + 'name'])

.. code-block:: python
    # Needed to instantiate new XML elements
    from xml.etree import ElementTree

    # Add new <action> to the <intent-filter> of BillingReceiver
    def androidmanifest_hook(root, namespace):
        receiver = root.find("application/receiver[@" + namespace + "name=" +
                             "'org.renpy.android.billing.BillingReceiver']")

        if receiver is not None:
            intent_filter = receiver.find("intent-filter")
            if intent_filter is not None:
                new = ElementTree.Element("action")
                new.attrib[namespace + "name"] = "com.android.DUMMY.EXAMPLE!"
                intent_filter.append(new)

To use the hook, provide your filename using --manifest-hook <filename> option
to build.py.

