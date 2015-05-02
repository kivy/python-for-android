package org.renpy.android;

import android.app.Activity;
import android.content.Context;
import android.view.View;
import android.view.ViewGroup;
import android.view.Gravity;
import android.widget.ArrayAdapter;
import android.widget.TextView;
import android.widget.LinearLayout;
import android.widget.ImageView;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;

public class ProjectAdapter extends ArrayAdapter<Project> {

    private Activity mContext;
    private ResourceManager resourceManager;
    
    
    public ProjectAdapter(Activity context) {
        super(context, 0);

        mContext = context;
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
