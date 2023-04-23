import datetime, subprocess, os, requests, yt_dlp

UNSPLASH_CLIENT_ID = "cKakzKM1cx44BUYBnEIrrgN_gnGqt81UcE7GstJEils"

def parse_timestamp(ts):
	formats = [
		"%M:%S", # MM:SS
		"%M:%S.%f", # MM:SS.mm
		"%S", # SS
		"%S.%f" # SS.mm
	]
	for f in formats:
		try:
			return (
				datetime.datetime.strptime(ts, f).replace(year=1970)
				- datetime.datetime(1970, 1, 1)
			).total_seconds()
		except ValueError:
			pass
	return None

def get_stock_images(fruit, image_count):
	r = requests.get(f"https://api.unsplash.com/search/photos?query={fruit}&per_page={image_count}&orientation=landscape&page=1&client_id={UNSPLASH_CLIENT_ID}").json()

	print(r.status_code)

	print(f'> Recieved {len(r["results"])} images')

	return [el["urls"]["regular"].split('?')[0] for el in r["results"]]

def generate_fruitcore(image_link, song_link, timestamp_from, timestamp_to, bitrate):
	bitrate = bitrate.lower().replace("bps","")

	try:
		r = requests.get(image_link)
		print(r.status_code)
		with open("fruit.png", "wb") as file:
			file.write(r.content)

		# Downloading and trimming audio

		ydl_opts = {
			'outtmpl': "download.%(ext)s",
			'format': 'mp3/bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
			}]
		}
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			ydl.download([song_link])

		if parse_timestamp(timestamp_to) != None:
			from_time = parse_timestamp(timestamp_from)
			to_time = parse_timestamp(timestamp_to) - from_time

			os.system(f"ffmpeg -ss {from_time} -i download.mp3 -t {to_time} -y trimmed_audio.mp3")
		else:
			to_time = None
			os.system("ffmpeg -i download.mp3 -y trimmed_audio.mp3")

		# Combine image and audio

		os.system(f'ffmpeg -loop 1 -i fruit.png -i trimmed_audio.mp3 -c:v libx264 -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -tune stillimage -c:a aac -b:a {bitrate} -pix_fmt yuv420p -shortest -y compiled.mp4')

		output = subprocess.check_output("ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 compiled.mp4", shell=True)
		print(f"> Resulting video length in seconds: {float(output)-2}")
		os.system(f"ffmpeg -ss 00:00 -i compiled.mp4 -to {float(output)-2} -c copy -y result.mp4")

		error = None
	except Exception as e:
		error = e

	# Clean up

	os.system("rm download.mp3")
	os.system("rm trimmed_audio.mp3")
	os.system("rm fruit.png")
	os.system("rm compiled.mp4")

	return error

if __name__ == "__main__":
	FRUIT_NAME = input("Choose fruit: ") or "mango"
	VIDEO_URL = input("Enter the song's YouTube link: ") or 'https://www.youtube.com/watch?v=X1E9bKNpJYM'
	FROM = input("Enter the timestamp to trim from (in format HH:MM:SS.xxx): ") or '0'
	TO = input("Enter the timestamp to trim to (in format HH:MM:SS.xxx): ") or '0'
	COMPRESSION = input("Enter a bitrate (e.g. 96k): ") or "128k"

	print(f"Putting fruit {FRUIT_NAME} over song url {VIDEO_URL} from {FROM} to {TO}")

	print('Please enter the index of the image you would like to use or "c" to enter a custom image link:')

	samples = get_stock_images(FRUIT_NAME, 10)

	for i, sample in enumerate(samples):
		print(f"{i}: {sample}")

	user_choice = ""
	while ( not user_choice.isnumeric() ) and user_choice != "c":
		user_choice = input("> ")

	if user_choice == "c":
		final_image_link = input("Custom image link: ")
	else:
		final_image_link = samples[int(user_choice)]

	generate_fruitcore(final_image_link, VIDEO_URL, FROM, TO, COMPRESSION)

	print("Done! :D")