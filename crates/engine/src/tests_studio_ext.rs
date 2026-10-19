//! Creative Studio: a native save gets `.3urood`, and a `.deckcraft` file (the same zip) still opens.

use crate::Session;
use crate::cmd::file::{WRITABLE_EXTENSIONS, format_for_path, open_presentation, writable_format_for_path};
use serde_json::json;

#[test]
fn native_save_is_3urood_and_deckcraft_still_opens() {
    assert_eq!(deckcraft_format::STUDIO_EXTENSION, "3urood");
    assert_eq!(WRITABLE_EXTENSIONS.first(), Some(&"3urood"), "3urood is listed first");
    assert_eq!(writable_format_for_path("deck.3urood"), Some("deckcraft"));
    assert_eq!(format_for_path("deck.3urood"), "deckcraft");

    let dir = std::env::temp_dir().join(format!("3urood-ext-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();

    let mut s = Session::with_new();
    let saved = dir.join("deck.3urood");
    s.execute("file.saveAs", &json!({"path": saved.to_string_lossy()})).unwrap();
    let bytes = std::fs::read(&saved).unwrap();
    assert!(deckcraft_format::sniff(&bytes), "the .3urood file is the native zip");
    assert!(open_presentation("deck.3urood", &bytes).is_ok());

    // The same bytes under the upstream name still open.
    let old = dir.join("old.deckcraft");
    std::fs::write(&old, &bytes).unwrap();
    assert!(open_presentation(&old.to_string_lossy(), &std::fs::read(&old).unwrap()).is_ok());

    let _ = std::fs::remove_dir_all(&dir);
}
