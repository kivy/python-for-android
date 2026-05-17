package org.kivy.android;

import android.content.Context;
import android.content.Intent;

public class PythonServiceIntent {

    private PythonServiceIntent() {}

    public static Intent build(
            Context ctx,
            Class<?> serviceClass,
            String serviceEntrypoint,
            String serviceTitle,
            String pythonName,
            String serviceStartAsForeground,
            String pythonServiceArgument,
            String smallIconName,
            String contentTitle,
            String contentText) {
        String appRoot = PythonUtil.getAppRoot(ctx);
        return buildWithPaths(
                ctx,
                serviceClass,
                ctx.getFilesDir().getAbsolutePath(),
                appRoot,
                null,
                serviceEntrypoint,
                serviceTitle,
                null,
                pythonName,
                serviceStartAsForeground,
                pythonServiceArgument,
                smallIconName,
                contentTitle,
                contentText);
    }

    public static Intent build(
            Context ctx,
            Class<?> serviceClass,
            String serviceEntrypoint,
            String serviceTitle,
            String pythonName,
            boolean serviceStartAsForeground,
            String pythonServiceArgument,
            String smallIconName,
            String contentTitle,
            String contentText) {
        return build(
                ctx,
                serviceClass,
                serviceEntrypoint,
                serviceTitle,
                pythonName,
                booleanToString(serviceStartAsForeground),
                pythonServiceArgument,
                smallIconName,
                contentTitle,
                contentText);
    }

    public static Intent buildActivityService(
            Context ctx,
            Class<?> serviceClass,
            String serviceEntrypoint,
            String serviceTitle,
            String serviceDescription,
            boolean serviceStartAsForeground,
            String pythonServiceArgument) {
        String appRoot = PythonUtil.getAppRoot(ctx);
        return buildWithPaths(
                ctx,
                serviceClass,
                ctx.getFilesDir().getAbsolutePath(),
                appRoot,
                null,
                serviceEntrypoint,
                serviceTitle,
                serviceDescription,
                "python",
                booleanToString(serviceStartAsForeground),
                pythonServiceArgument,
                null,
                null,
                null);
    }

    public static Intent buildWithPaths(
            Context ctx,
            Class<?> serviceClass,
            String androidPrivate,
            String androidArgument,
            String androidUnpack,
            String serviceEntrypoint,
            String serviceTitle,
            String serviceDescription,
            String pythonName,
            String serviceStartAsForeground,
            String pythonServiceArgument,
            String smallIconName,
            String contentTitle,
            String contentText) {
        Intent intent = new Intent(ctx, serviceClass);
        intent.putExtra("androidPrivate", androidPrivate);
        intent.putExtra("androidArgument", androidArgument);
        intent.putExtra("serviceEntrypoint", serviceEntrypoint);
        intent.putExtra("pythonName", pythonName);
        intent.putExtra("serviceStartAsForeground", serviceStartAsForeground);
        intent.putExtra("pythonHome", androidArgument);
        intent.putExtra("pythonPath", androidArgument + ":" + androidArgument + "/lib");
        intent.putExtra("pythonServiceArgument", pythonServiceArgument);
        intent.putExtra("serviceTitle", serviceTitle);

        if (androidUnpack != null) {
            intent.putExtra("androidUnpack", androidUnpack);
        }
        if (serviceDescription != null) {
            intent.putExtra("serviceDescription", serviceDescription);
        }
        if (smallIconName != null) {
            intent.putExtra("smallIconName", smallIconName);
        }
        if (contentTitle != null) {
            intent.putExtra("contentTitle", contentTitle);
        }
        if (contentText != null) {
            intent.putExtra("contentText", contentText);
        }

        return intent;
    }

    public static Intent buildWithPaths(
            Context ctx,
            Class<?> serviceClass,
            String androidPrivate,
            String androidArgument,
            String androidUnpack,
            String serviceEntrypoint,
            String serviceTitle,
            String serviceDescription,
            String pythonName,
            boolean serviceStartAsForeground,
            String pythonServiceArgument,
            String smallIconName,
            String contentTitle,
            String contentText) {
        return buildWithPaths(
                ctx,
                serviceClass,
                androidPrivate,
                androidArgument,
                androidUnpack,
                serviceEntrypoint,
                serviceTitle,
                serviceDescription,
                pythonName,
                booleanToString(serviceStartAsForeground),
                pythonServiceArgument,
                smallIconName,
                contentTitle,
                contentText);
    }

    public static void stop(Context ctx, Class<?> serviceClass) {
        ctx.stopService(new Intent(ctx, serviceClass));
    }

    private static String booleanToString(boolean value) {
        return value ? "true" : "false";
    }
}
