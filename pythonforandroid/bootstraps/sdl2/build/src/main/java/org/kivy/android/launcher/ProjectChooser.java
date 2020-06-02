package org.kivy.android.launcher;

import android.app.Activity;

import android.content.Intent;
import android.view.View;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.AdapterView;
import android.os.Environment;

import java.io.File;
import java.util.Arrays;
import android.net.Uri;

import org.renpy.android.ResourceManager;

public class ProjectChooser extends Activity implements AdapterView.OnItemClickListener {

    ResourceManager resourceManager;

    String urlScheme;

    @Override
    public void onStart()
    {
        super.onStart();

        resourceManager = new ResourceManager(this);

        urlScheme = resourceManager.getString("urlScheme");

        // Set the window title.
        setTitle(resourceManager.getString("appName"));

        // Scan the sdcard for files, and sort them.
        File dir = new File(Environment.getExternalStorageDirectory(), urlScheme);

        File entries[] = dir.listFiles();

        if (entries == null) {
            entries = new File[0];
        }

        Arrays.sort(entries);

        // Create a ProjectAdapter and fill it with projects.
        ProjectAdapter projectAdapter = new ProjectAdapter(this);

        // Populate it with the properties files.
        for (File d : entries) {
            Project p = Project.scanDirectory(d);
            if (p != null) {
                projectAdapter.add(p);
            }
        }

        if (projectAdapter.getCount() != 0) {        

            View v = resourceManager.inflateView("project_chooser");
            ListView l = (ListView) resourceManager.getViewById(v, "projectList");

            l.setAdapter(projectAdapter);                
            l.setOnItemClickListener(this);

            setContentView(v);

        } else {

            View v = resourceManager.inflateView("project_empty");
            TextView emptyText = (TextView) resourceManager.getViewById(v, "emptyText");

            emptyText.setText("No projects are available to launch. Please place a project into " + dir + " and restart this application. Press the back button to exit.");

            setContentView(v);
        }
    }

    public void onItemClick(AdapterView parent, View view, int position, long id) {
        Project p = (Project) parent.getItemAtPosition(position);

        Intent intent = new Intent(
                "org.kivy.LAUNCH",
                Uri.fromParts(urlScheme, p.dir, ""));

        intent.setClassName(getPackageName(), "org.kivy.android.PythonActivity");
        this.startActivity(intent);
        this.finish();
    }
}
