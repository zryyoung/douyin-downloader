package com.download.douyin.util;

import android.app.Service;
import android.content.Intent;
import android.content.Context;
import android.util.Log;
import android.widget.Toast;
import android.content.ClipData;
import android.content.ClipboardManager;
import java.util.Arrays;


public class TermuxExecuUtil {

    public static void run(Context context, String command) {
        try {
            
            Intent intent = new Intent();
            intent.setClassName("com.termux", "com.termux.app.RunCommandService");
            intent.setAction("com.termux.RUN_COMMAND");

            // 准备 bash -c 的参数
            String[] args = {"-c", command};

            // Java String[] 构造
            Class<String> stringClass = String.class;
            String[] javaStringArray = new String[args.length];

            System.arraycopy(args, 0, javaStringArray, 0, args.length);

            // 将命令复制到剪贴板
            ClipboardManager clipboard = (ClipboardManager) context.getSystemService(Context.CLIPBOARD_SERVICE);
            ClipData clip = ClipData.newPlainText("Termux Command", Arrays.toString(javaStringArray));
           // clipboard.setPrimaryClip(clip);
            
            intent.putExtra("com.termux.RUN_COMMAND_PATH", "/data/data/com.termux/files/usr/bin/bash");
            intent.putExtra("com.termux.RUN_COMMAND_ARGUMENTS", javaStringArray);
            intent.putExtra("com.termux.RUN_COMMAND_WORKDIR", "/data/data/com.termux/files/home");
            intent.putExtra("com.termux.RUN_COMMAND_BACKGROUND", false);
            intent.putExtra("com.termux.RUN_COMMAND_SESSION_ACTION", "0");
            context.startService(intent);
            Log.d("TermuxCommandExecutor", "执行命令成功：" + command);
            clip = ClipData.newPlainText("Termux Command", command);
            clipboard.setPrimaryClip(clip);
            //Toast.makeText(context, "执行命令成功：" + command, Toast.LENGTH_SHORT).show();
            
        } catch (Exception e) {
            Toast.makeText(context, "无法执行 Termux 命令，请确认已授权:\n" +
                "请确保 Termux 应用已安装并且权限已授权.", Toast.LENGTH_LONG).show();
            Log.e("TermuxCommandExecutor", "termuxRun 错误: " + e.getMessage(), e);
        }
    }
}
