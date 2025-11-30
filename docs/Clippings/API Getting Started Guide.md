---
title: "API Getting Started Guide"
source: "https://docs.dev.runwayml.com/guides/using-the-api/"
author:
  - "[[Runway API]]"
published:
created: 2025-11-28
description: "Learn how to use Runway's API for AI video generation. Follow our step-by-step guide to integrate Gen-4, image generation and more into your apps."
tags:
  - "clippings"
---
### Talking to the API

[Section titled “Talking to the API”](https://docs.dev.runwayml.com/guides/using-the-api/#talking-to-the-api)

You can use the [Playground](https://dev.runwayml.com/playground) to test your code, or follow the examples below to get started.

- [Generating Video](https://docs.dev.runwayml.com/guides/using-the-api/#pill-tab-panel-0)
- [Generating Images](https://docs.dev.runwayml.com/guides/using-the-api/#pill-tab-panel-1)

In this example, we’ll use the `gen4_turbo` model to generate a video from an image using the text prompt “A timelapse on a sunny day with clouds flying by”. When building this into your app, you’ll want to replace the `promptImage` with a URL of an image and a `promptText` with your own text prompt.

- [Node](https://docs.dev.runwayml.com/guides/using-the-api/#tab-panel-15)
- [Python](https://docs.dev.runwayml.com/guides/using-the-api/#tab-panel-16)
- [Just testing](https://docs.dev.runwayml.com/guides/using-the-api/#tab-panel-17)

First, you’ll want to install the Runway SDK. You can do this with npm:

Terminal window

```
npm install --save @runwayml/sdk
```

In your code, you can now import the SDK and start making requests:

```
import RunwayML, { TaskFailedError } from '@runwayml/sdk';
const client = new RunwayML();
// Create a new image-to-video task using the "gen4_turbo" modeltry {  const task = await client.imageToVideo    .create({      model: 'gen4_turbo',      // Point this at your own image file      promptImage: 'https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_(cropped).jpg',      promptText: 'A timelapse on a sunny day with clouds flying by',      ratio: '1280:720',      duration: 5,    })    .waitForTaskOutput();
  console.log('Task complete:', task);} catch (error) {  if (error instanceof TaskFailedError) {    console.error('The video failed to generate.');    console.error(error.taskDetails);  } else {    console.error(error);  }}
```

First, you’ll want to install the Runway SDK. You can do this with pip:

Terminal window

```
pip install runwayml
```

In your code, you can now import the SDK and start making requests:

```
from runwayml import RunwayML, TaskFailedError
client = RunwayML()
# Create a new image-to-video task using the "gen4_turbo" modeltry:  task = client.image_to_video.create(    model='gen4_turbo',    # Point this at your own image file    prompt_image='https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_(cropped).jpg',    prompt_text=' timelapse on a sunny day with clouds flying by',    ratio='1280:720',    duration=5,  ).wait_for_task_output()
  print('Task complete:', task)except TaskFailedError as e:  print('The video failed to generate.')  print(e.task_details)
```

If you’re not ready to start writing code, you can test the API with cURL.

Terminal window

```
# Replace the example URL below with your own image URLcurl -X POST https://api.dev.runwayml.com/v1/image_to_video \  -d '{    "promptImage": "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_(cropped).jpg",    "promptText": " timelapse on a sunny day with clouds flying by",    "model": "gen4_turbo",    "ratio": "1280:720",    "duration": 5  }' \  -H "Content-Type: application/json" \  -H "Authorization: Bearer $RUNWAYML_API_SECRET" \  -H "X-Runway-Version: 2024-11-06"
```

This command will start an image-to-video task using the “gen4\_turbo” model. You’ll see a JSON response with the task ID printed in your terminal, which you can use to fetch the task status.

#### Uploading base64 encoded images as data URIs

[Section titled “Uploading base64 encoded images as data URIs”](https://docs.dev.runwayml.com/guides/using-the-api/#uploading-base64-encoded-images-as-data-uris)

You can also upload base64 encoded images (as a data URI) instead of pointing to an external URL. This can be useful if you’re working with a local image file and want to avoid an extra network round trip to upload the image.

To do this, simply pass the base64 encoded image string as a data URI in the `promptImage` field instead of a URL. For more information about file types and size limits, see the [Inputs](https://docs.dev.runwayml.com/assets/inputs) page.

- [Node](https://docs.dev.runwayml.com/guides/using-the-api/#tab-panel-18)
- [Python](https://docs.dev.runwayml.com/guides/using-the-api/#tab-panel-19)

```
import fs from 'node:fs';import RunwayML, { TaskFailedError } from '@runwayml/sdk';
const client = new RunwayML();
// Read the image file into a Buffer. Replace \`example.png\` with your own image path.const imageBuffer = fs.readFileSync('example.png');
// Convert to a data URI. We're using \`image/png\` here because the input is a PNG.const dataUri = \`data:image/png;base64,${imageBuffer.toString('base64')}\`;
// Create a new image-to-video task using the "gen4_turbo" modeltry {  const imageToVideo = await client.imageToVideo    .create({      model: 'gen4_turbo',      // Point this at your own image file      promptImage: dataUri,      promptText: 'A timelapse on a sunny day with clouds flying by',      ratio: '1280:720',      duration: 5,    })    .waitForTaskOutput();
  console.log('Task complete:', task);} catch (error) {  if (error instanceof TaskFailedError) {    console.error('The video failed to generate.');    console.error(error.taskDetails);  } else {    console.error(error);  }}
```