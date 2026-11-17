use bellman::groth16::{create_proof, generate_parameters, VerifyingKey};
use impossible_player::{
    derive, encode_proof, fr, g1, g2, verify, MintCircuit, Proof, Public, CLAIM,
};
use pairing::bls12_381::{Bls12, Fr};
use pairing::{CurveAffine, CurveProjective, Field, PrimeField};
use std::error::Error;
use std::fs::File;
use std::io::{Read, Write};
use std::net::{Shutdown, TcpStream};

// const REMOTE: &str = "127.0.0.1:31337";
const CEREMONY_ID: &str = "3c311d9dfb7735e42643f394dc2c10af";
const TAU: &str = "3894627051107121998319229043008213446770981528672674568925122813412699817";
const REMOTE: &str = "impossible-dca9ed786b68.chall.nnsc.tf:1337";

fn submit(proof: Proof) -> std::io::Result<String> {
    let payload = encode_proof(&proof);
    print!("Submitting proof: {payload}\n");
    let mut stream = TcpStream::connect(REMOTE)?;
    stream.write_all(payload.as_bytes())?;
    stream.write_all(b"\n")?;
    stream.shutdown(Shutdown::Write)?;
    let mut response = String::new();
    stream.read_to_string(&mut response)?;
    Ok(response)
}

fn forge_proof() -> Result<Proof, Box<dyn Error>> {
    let tau = Fr::from_str(TAU).unwrap();
    let [alpha, beta, gamma, delta, g1_scale, g2_scale] = derive(tau);

    let params = generate_parameters::<Bls12, _>(
        MintCircuit {
            amount: None,
            balance: None,
        },
        g1(g1_scale).into_projective(),
        g2(g2_scale).into_projective(),
        alpha,
        beta,
        gamma,
        delta,
        tau,
    )?;

    let mut vk_file = File::open("vk.bin")?;
    let vk = VerifyingKey::<Bls12>::read(&mut vk_file)?;

    let mut inner = create_proof::<Bls12, _, _>(
        MintCircuit {
            amount: Some(fr(100)),
            balance: Some(fr(100)),
        },
        &params,
        Fr::zero(),
        Fr::zero(),
    )?;

    let mut correction = fr(CLAIM);
    correction.sub_assign(&fr(100));
    correction.mul_assign(&gamma);
    correction.mul_assign(&delta.inverse().unwrap());

    let ic2 = params.vk.ic[1];
    let correction_point = ic2.mul(correction.into_repr());
    let mut c = inner.c.into_projective();
    c.sub_assign(&correction_point);
    inner.c = c.into_affine();

    let proof = Proof {
        ceremony_id: CEREMONY_ID.to_owned(),
        claim: CLAIM,
        inner,
    };
    let public = Public {
        ceremony_id: CEREMONY_ID.to_owned(),
        vk,
    };
    assert!(
        verify(&public, &proof),
        "forged proof failed local verification"
    );

    Ok(proof)
}

fn main() -> Result<(), Box<dyn Error>> {
    let proof = forge_proof()?;
    let response = submit(proof)?;
    print!("{response}");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn forged_proof_verifies() {
        forge_proof().unwrap();
    }
}
