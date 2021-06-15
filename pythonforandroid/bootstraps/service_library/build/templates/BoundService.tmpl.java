package {{ args.package }};

import org.kivy.android.PythonBoundService;

public class {{ name|capitalize }}BoundService extends PythonBoundService {

    public {{ name|capitalize }}BoundService() {
        super();
        setPythonName("{{ name }}");
        setWorkerEntrypoint("{{ entrypoint }}");
    }
}
