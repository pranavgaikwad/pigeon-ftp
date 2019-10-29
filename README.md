# Pigeon FTP

![Pigeon FTP](./pigeon.png)

---

Pigeon FTP is a network protocol which provides a sophisticated point-to-multipoint data transfer.

Under the hood, it uses UDP to send packets from one host to another. Stop-and-Wait Automatic Repeat Request scheme implemented on top of UDP guarantees reliable data transfer.

## Installation

#### Clone this repo 

```bash
git clone git@github.ncsu.edu:pmgaikwa/pigeon-ftp pigeon-ftp

# switch to directory
cd pigeon-ftp
```

#### Install virtualenv on your box

```bash
pip --user install virtualenv
```

#### Create virtualenv

```bash
# create virtualenv
virtualenv --python=<path_to_python_3.7_executable> venv		# starts a virtualenv in "pigeon-ftp" directory
```

#### Start virtualenv

```bash
# start venv
source venv/bin/activate
```

#### Install

```bash
python setup.py install
```

```bash
pip install -r requirements.txt
```

## Testing

```bash
python setup.py test
```

## Documentation

Find all the relevant documentation in [docs](./docs) directory.
