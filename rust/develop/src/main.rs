extern crate oath;
extern crate securedrop_api;

use std::env;

use oath::{totp_now, HashType};
use securedrop_api::auth::UserPassOtp;
use securedrop_api::client::Client;

fn main() {
    // b32: JHCOGO7VCER3EJ4L
    let otp_secret = "49C4E33BF51123B2278B";
    let token = totp_now(otp_secret, 6, 0, 30, &HashType::SHA1).unwrap();

    let creds = UserPassOtp::new(
        "journalist".into(),
        "WEjwn8ZyczDhQSK24YKM8C9a".into(),

    );

    let args = env::args().collect::<Vec<String>>();
    let source_url = args[1].parse().unwrap();
    let journo_url = args[2].parse().unwrap();

    let client = Client::new(journo_url, creds, None).unwrap();
}
