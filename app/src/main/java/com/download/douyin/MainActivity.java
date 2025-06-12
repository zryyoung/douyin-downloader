package com.download.douyin;

import android.Manifest;
import android.content.pm.PackageManager;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.Toast;
import android.text.TextUtils;
import com.download.douyin.databinding.ActivityMainBinding;
import com.download.douyin.util.*;

import android.content.Intent;
import android.net.Uri;
import android.os.PowerManager;
import android.provider.Settings;
import android.app.Activity;
import android.content.Context;

import com.chaquo.python.Kwarg; 
import com.chaquo.python.PyObject;
import com.chaquo.python.android.AndroidPlatform;
import com.chaquo.python.Python;

import java.util.*;
import java.io.*;
import java.lang.StringBuilder;
import org.yaml.snakeyaml.Yaml;
import com.download.douyin.util.PermissionUtil;
// 创建线程，Runnable 接口
import java.lang.Thread;
// 用于将任务提交到线程池中执行（推荐使用）
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
// 用于线程安全处理结果，比如主线程更新 UI
import android.os.Handler;
import android.os.Looper;

public class MainActivity extends AppCompatActivity {
    private ActivityMainBinding binding;
    private static final String CONFIG_PATH = "/data/data/com.download.douyin/files/chaquopy/AssetFinder/app/config.yml";
    private static final int REQUEST_CODE_STORAGE = 1001;
    
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Inflate and get instance of binding
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        // Set content view to binding's root
        setContentView(binding.getRoot());
        // Setup onClick listeners
        setupListeners();
       
        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
       // 获取 Python 运行环境
        Python py = Python.getInstance();
      PyObject result = py.getModule("my").callAttr("say_hello");
      String message = result.toString().trim();
Toast.makeText(this, message, Toast.LENGTH_LONG).show();

checkAndRequestStoragePermission();

// 读取 YAML 配置
        readConfigAndSetUI();
        // ignoreBatteryOptimizations();
        
    }

private void readConfigAndSetUI() {
    try {
        File configFile = new File(CONFIG_PATH);
        if (!configFile.exists()) {
            Toast.makeText(this, "配置文件不存在", Toast.LENGTH_SHORT).show();
            return;
        }

        InputStream input = new FileInputStream(configFile);
        Yaml yaml = new Yaml();
        Map<String, Object> data = yaml.load(input);

        List<String> linkList = (List<String>) data.getOrDefault("link", new ArrayList<>());
        String videoLink = TextUtils.join("\n", linkList);  // 多行显示链接
        String cookie = (String) data.getOrDefault("cookie", "");
        String savePath = (String) data.getOrDefault("path", "/sdcard/Download/抖音主页作品/");

        binding.linkEditText.setText(videoLink);
        binding.CookieEditText.setText(cookie);
        binding.SaveEditText.setText(savePath);

    } catch (Exception e) {
        e.printStackTrace();
        Toast.makeText(this, "读取配置失败: " + e.getMessage(), Toast.LENGTH_LONG).show();
    }
}

private void checkAndRequestStoragePermission() {
        if (!PermissionUtil.hasStoragePermission(this)) {
            PermissionUtil.requestStoragePermission(this);
        } else {
            //Toast.makeText(this, "已获得存储权限", Toast.LENGTH_SHORT).show();
        }
    }

    // 回调权限请求结果
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PermissionUtil.REQUEST_CODE_STORAGE) {
            if (PermissionUtil.hasStoragePermission(this)) {
                Toast.makeText(this, "权限申请成功", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, "权限被拒绝", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void setupListeners() {
    binding.downloadButton.setOnClickListener(
        new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ignoreBatteryOptimizations();
                // 获取输入
                String videoLink = extractVideoLink(binding.linkEditText.getText().toString());
                String savePath = binding.SaveEditText.getText().toString();
                String cookie = binding.CookieEditText.getText().toString();

                // 检查必填项
                if (!videoLink.isEmpty() && !savePath.isEmpty()) {
                    // 保存配置
                    saveConfig(videoLink, cookie, savePath);

                    // 提示开始下载
                    Toast.makeText(MainActivity.this, "正在下载主页视频: " + videoLink, Toast.LENGTH_SHORT).show();

                    // 开启子线程执行下载
                    new Thread(() -> {
                        try {
                            Python py = Python.getInstance();
                            PyObject module = py.getModule("main");

                            // 拼接参数
                            StringBuilder argsBuilder = new StringBuilder();
                            argsBuilder.append("-C,True");

                            // 多个链接处理
                            String[] linksArray = videoLink.split("\n");
                            for (String link : linksArray) {
                                argsBuilder.append(",-l,").append(link.trim());
                            }

                            argsBuilder.append(",-p,").append(savePath);

                            // 如果 cookie 非空则添加
                            if (!cookie.isEmpty()) {
                                argsBuilder.append(",--cookie,").append(cookie);
                            } else {
                                runOnUiThread(() ->
                                    Toast.makeText(MainActivity.this, "未填写 Cookie，仅下载最新的作品", Toast.LENGTH_SHORT).show()
                                );
                            }

                            // 调用 Python
                            String args = argsBuilder.toString();
                            PyObject result = module.callAttr("main", args);

                        } catch (Exception e) {
                            e.printStackTrace();
                            try {
                                FileWriter writer = new FileWriter("/sdcard/error_log.txt", true);
                                writer.write("Error: " + e.toString() + "\n");
                                for (StackTraceElement element : e.getStackTrace()) {
                                    writer.write("    at " + element.toString() + "\n");
                                }
                                writer.close();
                            } catch (IOException ioException) {
                                ioException.printStackTrace();
                            }
                        }
                    }).start();

                } else {
                    Toast.makeText(MainActivity.this, "请输入视频链接和保存路径", Toast.LENGTH_SHORT).show();
                }
            }
        });

    // 删除 cookie 按钮
    binding.deleteCookieButton.setOnClickListener(
        new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                deleteCookie();
            }
        });
}

private void saveConfig(String videoLink, String cookie, String savePath) {
    try {
        File configFile = new File(CONFIG_PATH);
        if (!configFile.exists()) {
            Toast.makeText(this, "配置文件不存在", Toast.LENGTH_SHORT).show();
            return;
        }

        List<String> newLinkLines = new ArrayList<>();
        for (String l : videoLink.split("\\r?\\n")) {
            if (!l.trim().isEmpty()) {
                newLinkLines.add("  - " + l.trim());
            }
        }

        List<String> lines = new ArrayList<>();
        BufferedReader reader = new BufferedReader(new FileReader(configFile));
        String line;
        boolean inLinkBlock = false;

        while ((line = reader.readLine()) != null) {
            String trimmed = line.trim();

            // 处理 link 列表替换
            if (trimmed.startsWith("link:")) {
                lines.add(line);  // 添加带注释的 link: 行
                inLinkBlock = true;
                continue;
            }

            if (inLinkBlock) {
                if (trimmed.startsWith("-")) {
                    // 跳过原有链接列表项
                    continue;
                } else if (trimmed.isEmpty()) {
                    continue;
                } else {
                    // 链接结束，插入新链接
                    for (String newLine : newLinkLines) {
                        lines.add(newLine);
                    }
                    inLinkBlock = false;
                    lines.add(line); // 加入当前非链接行
                }
            } else if (trimmed.startsWith("path:")) {
                // 替换 path 行
                String prefix = line.substring(0, line.indexOf("path:"));
                lines.add(prefix + "path: " + savePath);
            } else if (trimmed.startsWith("cookie:")) {
                // 替换 cookie 行
                String prefix = line.substring(0, line.indexOf("cookie:"));
                lines.add(prefix + "cookie: \"" + cookie + "\"");
            } else {
                lines.add(line);
            }
        }

        // 如果 link 是最后一项，要在末尾补上新链接
        if (inLinkBlock) {
            for (String newLine : newLinkLines) {
                lines.add(newLine);
            }
        }

        reader.close();

        BufferedWriter writer = new BufferedWriter(new FileWriter(configFile));
        for (String l : lines) {
            writer.write(l);
            writer.newLine();
        }
        writer.close();

        Toast.makeText(this, "配置已保存（结构保留）", Toast.LENGTH_SHORT).show();

    } catch (IOException e) {
        e.printStackTrace();
        Toast.makeText(this, "保存配置失败: " + e.getMessage(), Toast.LENGTH_LONG).show();
    }
}

    private String extractVideoLink(String message) {
        // 指定要查找的链接前缀
        String prefix = "https://v.douyin.com/";
        // 首先检查 message 是否以 prefix 开头
        if (!message.startsWith(prefix)) {
            
            // 查找链接的起始位置
            int startIndex = message.indexOf(prefix);

            if (startIndex != -1) { // 如果找到了前缀
                // 找到下一个空格或换行符的索引
                int endIndex = message.indexOf(" ", startIndex);
                if (endIndex == -1) { // 如果没有找到空格，则链接到字符串结束
                    endIndex = message.length();
                }
                // 提取链接并返回
                return message.substring(startIndex, endIndex);
            }
            return null; // 未找到链接
        }
        return message;
    }

    
private void downloadVideo() {
        try {
            Python py = Python.getInstance();
            PyObject module = py.getModule("main");
        String videoLink = binding.linkEditText.getText().toString();
        String cookie = binding.CookieEditText.getText().toString();
        if (cookie.isEmpty()) {
    Toast.makeText(this, "Cookie 为空，无法获取全部作品。", Toast.LENGTH_LONG).show();
    // 这里可以设置默认行为，例如继续只获取最新的20个作品，或者提示用户填写 cookie
} else {
    // 使用 cookie 下载全部作品
}
        String savePath = binding.SaveEditText.getText().toString();
        // 这里执行下载的相关代码，可以调用Python脚本等
        // 拼接参数字符串，用逗号隔开
        //String args = "-C,True,-l," + videoLink + ",-p," + savePath + ",--cookie," + cookie;
        // 拼接参数字符串
        StringBuilder argsBuilder = new StringBuilder();
        argsBuilder.append("-C,True");

// 分割字符串到数组一条或者多条链接
        String[] linksArray = videoLink.split("\n");
        // 处理多个视频链接，拼接成 -l link1 -l link2 形式
        for (String link : linksArray) {
            argsBuilder.append(",-l,").append(link.trim()); // 使用 trim() 去掉多余空格
        }

        // 添加其他参数
        argsBuilder.append(",-p,").append(savePath)
            .append(",--cookie,").append(cookie);

        // 将构建的参数字符串设置到 args
        String args = argsBuilder.toString();
PyObject result = module.callAttr("main",args);//, argsList.toArray());
//String message = result.toString().trim();
//Toast.makeText(this, message, Toast.LENGTH_LONG).show();
        
        } catch (Exception e) {
            e.printStackTrace(); // 控制台输出
            try {
                FileWriter writer = new FileWriter("/sdcard/error_log.txt", true); // 追加模式
                writer.write("Error: " + e.toString() + "\n");
                for (StackTraceElement element : e.getStackTrace()) {
                    writer.write("    at " + element.toString() + "\n");
                }
                writer.close();
            } catch (IOException ioException) {
                ioException.printStackTrace(); // 写日志失败的错误
            }
        }
    }

    private void deleteCookie() {
        binding.CookieEditText.setText("");
        Toast.makeText(this, "cookie 已删除", Toast.LENGTH_SHORT).show();
    }

    private void ignoreBatteryOptimizations() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
            String packageName = getPackageName();
            if (!pm.isIgnoringBatteryOptimizations(packageName)) {
                Intent intent = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS);
                intent.setData(Uri.parse("package:" + packageName));
                startActivity(intent); // 会弹出一个系统对话框，请求用户手动授权
            }
        }
    }


    @Override
    protected void onDestroy() {
        super.onDestroy();
        this.binding = null;
    }
    
    @Override
    protected void onStart() {
        super.onStart();
        ignoreBatteryOptimizations();
    }
}
