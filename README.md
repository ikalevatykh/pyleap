# pyleap
Helper tools for Leap Motion devices

## Install

### Install Leap Motion SDK

Download and install [Leap Motion V2 SDK](https://www2.leapmotion.com/v2-developer-beta-linux)

### Install package from source code

Supported python version >= 3.7

```
git clone https://github.com/ikalevatykh/pyleap.git
cd pyleap
python setup.py install
```

## Start leapd server

`sudo leapd` - start server before using the package.

## Tools

- `python -m pyleap.tools.dump --file {pickle_file}` - record frames from the Leap Motion device to an output pickle file.
- `python -m pyleap.tools.show` - visualise frames from a real Leap Motion device.
- `python -m pyleap.tools.show --file {pickle_file}` - visualise frames from a prerecorded pickle file.


## License

*pyleap* is licensed under the MIT License - see the LICENSE file for details.
