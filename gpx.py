"""GPX CLI
Usage:
    gpx.py
    gpx.py copy <in> <out> [--time_start=<time_start>] [--date_start=<date_start>]
    gpx.py -h|--help
    gpx.py -v|--version
Options:
    --date_start=<date_start> Set date start
    --time_start=<time_start>  Set time start and correct time of any track pts
    -h --help  Show this screen.
    -v --version  Show version.
"""

from docopt import docopt
import arrow
import xmltodict
from collections import OrderedDict
from copy import deepcopy


def copy_gpx(in_file, out_file, date_adjust, time_adjust):
    print(f"copy from {in_file} to {out_file}  adjust start date: {date_adjust} time: {time_adjust}")
    doc2 = OrderedDict()
    time_shift = None
    with open(in_file) as fd:
        doc = xmltodict.parse(fd.read())

        if date_adjust or time_adjust:
            try:
                first_date = arrow.get(doc['gpx']['trk']['trkseg']['trkpt'][0]['time'])
                # get date
                date_str = first_date.format('YYYY-MM-DD')

                # get time
                time_str = first_date.format('HH:mm:ss')

                # zone str
                zone_str = first_date.format('ZZ')

                # create new time
                if date_adjust:
                    new_date = date_adjust
                else:
                    new_date = date_str

                if time_adjust:
                    new_date = "".join([new_date, "T", time_adjust, zone_str])
                else:
                    new_date = "".join([new_date, "T", time_str, zone_str])

                # find offset and set date adjust
                new_date_obj = arrow.get(new_date)
                time_shift = (new_date_obj - first_date).total_seconds()

                print(f"First date is Zone {zone_str}, time {time_str}, date {date_str} "
                      f"new date = {new_date} shift: {time_shift}")

            except AttributeError:
                time_shift = None
                print("No time adjustment possible can't find time")
        doc2['gpx'] = OrderedDict()
        for gpx, gpx_value in doc['gpx'].items():
            if gpx == 'trk':
                doc2['gpx']['trk'] = OrderedDict()
                for seg, seg_value in gpx_value.items():
                    if seg == 'trkseg':
                        doc2['gpx']['trk'][seg] = OrderedDict()
                        print(f'   {seg}')
                        doc2['gpx']['trk'][seg]['trkpt'] = []
                        for trkpt, trkpt_values in seg_value.items():
                            for trkpt_value in trkpt_values:
                                trk_item = OrderedDict()
                                for trkpt_ele, trkpt_ele_value in trkpt_value.items():
                                    if trkpt_ele == 'time' and time_shift:
                                        trkpt_ele_value = arrow.get(trkpt_ele_value).shift(seconds=time_shift)
                                    trk_item[trkpt_ele] = trkpt_ele_value
                                trk_item['desc'] = '{"DBK": 0.0, "COM": 0, "STW": 0.0, "ENG": "on", "Note": ""}'
                                doc2['gpx']['trk'][seg]['trkpt'].append(trk_item)
                                print(f'          {trkpt} -- {trk_item}')
                    else:
                        doc2['gpx']['trk'][seg] = seg_value
                        print(f'   {seg} -- {seg_value}')

            else:
                doc2['gpx'][gpx] = gpx_value
                print(f'{gpx} -- {gpx_value}')

    with open(out_file, "x") as fd_out:
        xmltodict.unparse(doc2, output=fd_out, encoding='utf-8', pretty=True,  indent="  ")


def parse_args(doc_ags):
    doc_args = docopt(__doc__, version='DEMO 1.0')
    in_file = doc_args.get('<in>')
    out_file = doc_args.get('<out>')
    time_adjust = doc_args.get('--time_start')
    date_adjust = doc_args.get('--date_start')
    if doc_args.get('copy') and in_file and out_file:
        copy_gpx(in_file, out_file, date_adjust, time_adjust)
    else:
        print(doc_args)


if __name__ == '__main__':
    parse_args(docopt(__doc__, version='DEMO 1.0'))



