.. _kivy_bootstrap_contract:

Supporting Kivy 3 (the Kivy bootstrap contract)
===============================================

Kivy 3 asks the bootstrap for the current Android ``Activity`` instead of
reflecting a class name of its own. Any tool that builds Android APKs — this
project, another build tool, or a bootstrap you write yourself — makes Kivy 3
work by answering that question.

This page is the implementer's guide: what to ship, the rules it must obey.
p4a's own implementation is
``pythonforandroid/recipes/android/src/_kivy_bootstrap.py``.

Kivy 2.3.1 does not use this contract and is unaffected; see
`Supporting Kivy 2.3.1 as well`_ if you need both.

What you ship
-------------

One pure-Python module named ``_kivy_bootstrap``, importable at the **top
level** of the running app's ``sys.path``. Nothing else: no registration call,
no import order to arrange, no Kivy dependency.

The name is Kivy's, not any bootstrap's. That is the point of the arrangement —
Kivy depends on the name, so it depends on no particular bootstrap, and an
unmodified Kivy runs on an APK built by any of them.

Kivy imports the module the first time it needs the Activity, so it must be on
``sys.path`` before the application's ``main.py`` runs. In p4a it is a
``py_modules`` entry of the ``android`` recipe, so it lands beside the app's
other top-level modules in ``site-packages``.

``get_activity()`` (required)
-----------------------------

Return the current ``android.app.Activity``, or ``None`` where there is none.

.. code-block:: python

    def get_activity():
        return SomeActivityClass.mActivity

Kivy calls this **live on every access** and never caches the result, so your
implementation must not cache it either (see rule 2 below). ``None`` is a
legitimate answer, not a failure: a background service runs with no Activity,
and Kivy treats that as the ordinary case it is.

``get_context()`` (optional)
----------------------------

Return an ``android.content.Context``, or ``None``.

Implement this only if your bootstrap runs processes that never have an
Activity and still need a Context. When it is absent — or returns ``None`` —
Kivy derives the Application context from the current Activity, which is
equivalent for everything Kivy uses a Context for. p4a does not implement it.

``remove_presplash()`` (optional)
---------------------------------

Dismiss your boot splash. Kivy calls this once it has drawn its first frame,
which is the one thing about a splash screen that only Kivy knows.

*How* a splash is dismissed is entirely yours, and the mechanisms differ
fundamentally: p4a overlays a ``View`` and removes it, while a bootstrap using
the Android 12 system splash releases a keep-on-screen condition instead — not
a method on the Activity at all. That is why this is an optional function on
your module rather than a method Kivy calls on the Activity.

If you have no splash to dismiss, omit the function. Kivy treats its absence as
the no-op it is, with no warning.

Rules
-----

1. **Never import Kivy from this module.** Kivy reads its ``KIVY_*``
   environment and builds its configuration at import time, so importing it
   before the application runs would freeze that configuration before the app's
   ``main.py`` could set it. Kivy pulls from you precisely so that you never
   have to import it.

2. **Never cache the Activity.** Android destroys and recreates the Activity on
   configuration changes (rotation, dark mode, locale, multi-window) and after
   process death. A stored instance goes stale, and holding one in a Python
   global pins a JNI reference to a dead Activity. Read it fresh on every call
   and staleness stops being your problem.

3. **Resolve reflection inside the call, not at import.** Resolve the Java
   class on first call and cache *the class* if you like, but do not do it at
   module import: a reflection failure would then surface from Kivy's discovery
   import, where it looks like a missing module rather than the real fault.

4. **Fail at import only with an ImportError, and only if you mean it.** Kivy
   treats ``ImportError`` as "this bootstrap does not implement the contract"
   and moves on to raise a diagnostic. Any *other* exception escaping your
   module's import is treated as a fault in your module and propagates
   unchanged, so it is not mistaken for an absent bootstrap.

5. **A presplash hook must not raise, and must tolerate repeat calls.**
   Kivy does not guard the call and makes no promise about calling it exactly
   once. Doing nothing is a correct outcome; raising is not.

6. **Hold no state beyond the resolved class.** Kivy may call these from more
   than one thread. A stateless module is thread-safe without a lock, and the
   contract is designed so that statelessness costs nothing.

What Kivy does with it
----------------------

Useful when debugging your implementation:

* The module is imported lazily, on first use, and the outcome is cached —
  including failure, so a build with no such module does not pay for a failed
  import on every geometry read.
* If the module is missing (or exposes no callable ``get_activity``) **while an
  Android runtime is present**, Kivy raises ``ActivityProviderMissing``. This
  is deliberately not caught by Kivy's display-geometry getters, which would
  otherwise mask a broken build as plausible-looking defaults.
* ``kivy.mobile.get_app_context()`` prefers your ``get_context()`` and
  otherwise calls ``getApplicationContext()`` on the current Activity.
* ``kivy.mobile.get_activity()`` returns exactly what your function returned,
  ``None`` included.

Supporting Kivy 2.3.1 as well
-----------------------------

Kivy 2.3.1 predates this contract. It reaches p4a's Python ``android`` module
directly — ``android.remove_presplash()`` and friends — and hardcodes
``org.kivy.android.PythonActivity``. A bootstrap that wants to run both Kivy
2.3.1 and Kivy 3 therefore has to satisfy both: ship ``_kivy_bootstrap`` for
Kivy 3, and provide the ``android`` module (and an activity of that class name)
for 2.3.1. A bootstrap targeting Kivy 3 alone needs only this contract.
