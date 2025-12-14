// Prevents additional console window on Windows in release builds
#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::{
    CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, SystemTrayMenuItem,
};

// Commands that can be called from JavaScript
#[tauri::command]
fn check_backend_status() -> Result<String, String> {
    // Check if backend is running
    match reqwest::blocking::get("http://localhost:8000/status") {
        Ok(_) => Ok("Backend is running".to_string()),
        Err(_) => Err("Backend is not running".to_string()),
    }
}

#[tauri::command]
fn open_backend_docs() {
    let _ = open::that("http://localhost:8000/docs");
}

fn main() {
    // System tray menu
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let hide = CustomMenuItem::new("hide".to_string(), "Hide");
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let docs = CustomMenuItem::new("docs".to_string(), "API Docs");
    let status = CustomMenuItem::new("status".to_string(), "System Status");

    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(status)
        .add_item(docs)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    let system_tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick {
                position: _,
                size: _,
                ..
            } => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
            SystemTrayEvent::MenuItemClick { id, .. } => {
                match id.as_str() {
                    "quit" => {
                        std::process::exit(0);
                    }
                    "hide" => {
                        let window = app.get_window("main").unwrap();
                        window.hide().unwrap();
                    }
                    "show" => {
                        let window = app.get_window("main").unwrap();
                        window.show().unwrap();
                        window.set_focus().unwrap();
                    }
                    "docs" => {
                        let _ = open::that("http://localhost:8000/docs");
                    }
                    "status" => {
                        let window = app.get_window("main").unwrap();
                        window.show().unwrap();
                        window.set_focus().unwrap();
                        // Navigate to status page if available
                    }
                    _ => {}
                }
            }
            _ => {}
        })
        .on_window_event(|event| match event.event() {
            tauri::WindowEvent::CloseRequested { api, .. } => {
                // Don't close, just hide to tray
                event.window().hide().unwrap();
                api.prevent_close();
            }
            _ => {}
        })
        .invoke_handler(tauri::generate_handler![
            check_backend_status,
            open_backend_docs
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
