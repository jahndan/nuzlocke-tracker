// cli entry point

use clap::Parser;
use xcap::Window;

// trying stuff
use opencv::prelude::*;

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

    let _imtest = image;

    // opencv testing??
    use opencv::core::{Point2f, RotatedRect, Size, Size2f};
	use opencv::imgproc;
    let rect = RotatedRect::new(Point2f::new(100., 100.), Size2f::new(100., 100.), 90.)?;
    println!("opencv testing??");
    // stuff
	let mut pts = Mat::default();
	imgproc::box_points(rect, &mut pts)?;
	let pts = pts.reshape_def(Point2f::opencv_channels())?;
    println!("stuff");
	// asserts
    assert_eq!(Size::new(1, 4), pts.size()?);
	assert_eq!(Point2f::new(50., 50.), *pts.at(0)?);
	assert_eq!(Point2f::new(150., 50.), *pts.at(1)?);
	assert_eq!(Point2f::new(150., 150.), *pts.at(2)?);
	assert_eq!(Point2f::new(50., 150.), *pts.at(3)?);
    println!("asserts!");

/* // imagebuffer iteration
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
*/

/* // FFT attempts
    use image::{ImageBuffer, DynamicImage};
    use nshare::*;
    use ndarray::Array2;
    use ndrustfft::{ndfft_r2c_par, Complex, R2cFftHandler};

    let (nx, ny) = (image.width() as usize, image.height() as usize);
    let impre = DynamicImage::ImageRgba8(image).to_luma32f();
    let mut impost = Array2::<Complex<f32>>::zeros((nx / 2 + 1, ny));
    let mut fft_handler = R2cFftHandler::<f32>::new(nx);
    ndftt_r2c_par(&impre.view(), &mut impost.view_mut(), &mut fft_handler, 0);
    let imt = impost.map(|z| z.norm());
*/

/* // match template attempts
    let needle = {
        use image::ImageReader;
        ImageReader::open("hoothoot.png")?.decode()?.to_luma8()
    };

    use image::{DynamicImage, imageops::FilterType};
    let haystack = DynamicImage::ImageRgba8(window.capture_image().unwrap());
    let haystack = haystack.resize(haystack.width(), haystack.height(), FilterType::Nearest).to_luma8();

    let result = {
        use imageproc::template_matching::{self, MatchTemplateMethod};
        template_matching::match_template_parallel(&haystack, &needle, MatchTemplateMethod::SumOfSquaredErrors)
    };

    use imageproc::template_matching;
    println!("{:?}", template_matching::find_extremes::<f32>(&result));
*/

    #[cfg(feature = "idbg")]
    {
        use show_image::{create_window, event::WindowEvent, event::VirtualKeyCode};
        // draw to new window
        let win = create_window("image", Default::default())?;

        println!("Press [Esc] to quit...");
        win.set_image("testing", _imtest)?;

        // stall until `Esc` pressed
        for event in win.event_channel()? {
            if let WindowEvent::KeyboardInput(event) = event {
                // println!("{:#?}", event); // logs keyboard events
                if event.input.key_code == Some(VirtualKeyCode::Escape) && event.input.state.is_pressed() {
                    break;
                }
            }
        }
    } // end idbg block

    Ok(())
}

/* // read from disk
use image::ImageReader;
let img = ImageReader::open("myimage.png")?.decode()?;
*/

/* // write to disk
use image::ImageBuffer
img.save(format!(
        "target/{}-capture.png",
        normalized(window.title())
    ))
    .unwrap();
*/
