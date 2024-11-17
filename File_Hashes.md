# Cryptographic Hashes

Beginning with v2.0.7, I'm providing the SHA256 cryptographic hash for the installer and the python source files.

While it is true that nothing can absolutely guarantee you will not be abused online, cryptographic hashes of files you download from the Internet can help.
They help by providing you a mechanism by which you can gain a reasonable amount of assurance the file you downloaded is the same file the developer created.
There is a **TON** of stuff you can know about hashes.  I'm going to line out here the gist of what I have read on the subject.

  - Modern hash algorithms like SHA256 are still very secure.  The older MD5 algorithm **can** be manipulated to trick you.
  - You need to acquire the hash you are comparing from a source **other** than where you got the file.
    - I'm posting hashes for my stuff at my blog site at [https://www.drgerg.com/pages/hashes.html](https://www.drgerg.com/pages/hashes.html).

Generating the hash value to compare is really simple.  Just make sure you provide the correct path to the downloaded file where you see 'filename' here below.

## Windows: 

  - using cmd terminal: CertUtil -hashfile filename SHA256
  - using PowerShell: Get-FileHash filename -Algorithm SHA256

## Linux:

  - sha256sum filename

## MacOS

  - shasum -a 256 filename

[Read more at security.stackexchange.com](https://security.stackexchange.com/questions/189000/how-to-verify-the-checksum-of-a-downloaded-file-pgp-sha-etc)

[Digital Signatures vs. Hashes](https://security.stackexchange.com/questions/31836/why-we-use-gpg-signatures-for-file-verification-instead-of-hash-values)

[Makeuseof: 7 Free Hash Checkers](https://www.makeuseof.com/tag/free-hash-checkers-file-integrity/)

[Cisco Talos File Reputation Checker](https://talosintelligence.com/talos_file_reputation)
