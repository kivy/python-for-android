package org.kivy.android.launcher;

import android.app.Activity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;
import android.widget.ImageView;

import org.renpy.android.ResourceManager;

public class ProjectAdapter extends ArrayAdapter<Project> {

    private ResourceManager resourceManager;
    
    public ProjectAdapter(Activity context) {
        super(context, 0);
        resourceManager = new ResourceManager(context);
    }

    public View getView(int position, View convertView, ViewGroup parent) {
        Project p = getItem(position);

        View v = resourceManager.inflateView("chooser_item");
        TextView title = (TextView) resourceManager.getViewById(v, "title");
        TextView author = (TextView) resourceManager.getViewById(v, "author");
        ImageView icon = (ImageView) resourceManager.getViewById(v, "icon");

        title.setText(p.title);
        author.setText(p.author);
        icon.setImageBitmap(p.icon);
        
        return v;        
    }
}
