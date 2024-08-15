// cli entry point

use clap::Parser;
use xcap::Window;

/// ?
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// ??
    #[arg(short, long)]
    window: String,
}

#[cfg_attr(feature = "idbg", show_image::main)]
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();

    // capturable windows (exclude minimized ones)
    let windows_iter = Window::all()
        .unwrap()
        .into_iter()
        .filter(|win| !win.is_minimized());

    // grabbing the first window that matches the user input
    let mut window: Option<Window> = None;
    for w in windows_iter {
        // need to verify which of these is to be checked against (also on other platforms)
        if w.title().contains(&args.window) || w.app_name().contains(&args.window) {
            window = Some(w);
            break;
        }
    }
    let window: Window = window.expect("Window not found!!");

    // print window info
    println!(
        "Window: {:?} {:?} {:?}",
        window.title(),
        (window.x(), window.y(), window.width(), window.height()),
        (window.is_minimized(), window.is_maximized())
    );

    // capture window -> ImageBuffer type from image
    let image = window.capture_image().unwrap();

    let mut i = 0;
    // 2d iteration over ImageBuffer
    for (x, y, pixel) in image.enumerate_pixels() {
        println!(
            "im({}, {}) = {:?}",
            y,
            x,
            pixel,
        );
        // capping the amount of output spit into stdout
        i += 1;
        if i >= 100 {
            break;
        }
    }

    #[cfg(feature = "idbg")]
    {
        use show_image::{create_window, event::WindowEvent, event::VirtualKeyCode};
        // draw to new window
        let win = create_window("image", Default::default())?;
        win.set_image("image-001", image)?;

        println!("Press [Esc] to quit...");

        // stall until `Esc` pressed
        for event in win.event_channel()? {
            if let WindowEvent::KeyboardInput(event) = event {
                // println!("{:#?}", event); // logs keyboard events
                if event.input.key_code == Some(VirtualKeyCode::Escape) && event.input.state.is_pressed()
                {
                    break;
                }
            }
        }
    } // end idbg block

    Ok(())
}

//// read from disk
// use image::ImageReader;
// let img = ImageReader::open("myimage.png")?.decode()?;

//// write to disk
// use image::ImageBuffer
// img
//     .save(format!(
//         "target/{}-capture.png",
//         normalized(window.title())
//     ))
//     .unwrap();
