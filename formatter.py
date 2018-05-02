from pearl.core import Clip, PearlError
from colorama import Fore, Style


class Clip_Formatter:
    def __init__(self, clip):
        # If the parameter is not <Clip> class, raise PearlError
        if type(clip) != Clip:
            err = '<Clip_Formatter> only receives <core.Clip> class.'
            raise PearlError(err)
        self.clip = clip

    def print_clip(self):
        # If the clip has not been sorted by title, raise PearlError
        if not self.clip._is_sorted:
            err = 'Cannot operate `print_clip` method.' + \
                  'Please try <Clip>.sort() method before using it.'
            raise PearlError(err)

        # Define frame
        top_frame = """
{title} | {detail_info}"
------------------------------------------------------
""".strip()
        time_frame = """
{start} - {end} | {avail_cap} / {total_cap} | {cinfo} ({hinfo})
""".strip()
        bottom_frame = """
------------------------------------------------------
""".strip()

        # Set <list> type variable `frame`
        frame = []

        # Draw table by adding strings on `frame`
        for movie in self.clip.data:
            # Add empty line
            frame.append('\n')

            # Colorize `TITLE` and draw top frame ::
            TITLE = \
                Fore.LIGHTBLUE_EX + Style.BRIGHT + \
                ' [' + movie['title'] + ']' + Style.RESET_ALL

            # Format Detail Info
            detail_info = ''
            if self.clip._contains_detail:
                detail_info = """
{genre} / {rate}
""".strip()

            frame.append(top_frame.format(
                title=title,
                detail_info=detail_info.format(**moive)))

            # Draw time frame ::
            for sc in self.clip.data[movie]:
                # Colorize `start`, and add additional whitespace at front
                sc['start'] = \
                    Fore.LIGHTBLUE_EX + " " + sc['start'] + Style.RESET_ALL

                # Colorize `avail_cap` based on its value,
                # and format `avail_cap` into 3-digit-string
                if sc['avail_cap'] < int(sc['total_cap'] / 4):
                    # If avail_cap is below 25% of total capacity :: RED
                    sc['avail_cap'] = \
                        Fore.LIGHTRED_EX + \
                        "%3d" % sc['avail_cap'] + \
                        Style.RESET_ALL
                elif sc['avail_cap'] < int(sc['total_cap'] / 2):
                    # If avail_cap is below 50% of total capacity :: YELLOW
                    sc['avail_cap'] = \
                        Fore.LIGHTYELLOW_EX + \
                        "%3d" % sc['avail_cap'] + \
                        Style.RESET_ALL
                else:
                    sc['avail_cap'] = \
                        Fore.LIGHTBLUE_EX + \
                        "%3d" % sc['avail_cap'] + \
                        Style.RESET_ALL

                # Format `total_cap` into 3-digit-string
                sc['total_cap'] = "%3d" % sc['total_cap']

                # Append Item
                frame.append(time_frame.format(**sc))

            # Draw bottom frame and add few empty lines ::
            frame.append(bottom_frame)
            frame.append('\n')

        # Print data
        print('\n'.join(frame))
