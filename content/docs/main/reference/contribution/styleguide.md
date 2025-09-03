---
title: Style guide
weight: 30
---

All documentation contributions in kgateway must follow general standards to ensure content is clear, concise, and understandable. 

## Language

All documentation content must be written in English. Currently, kgateway does not support other languages. 

## Sentence case

Use sentence case for any content that you add. Sentence case means to capitalize the first word in a sentence and end with a punctuation mark like a period. Do not capitalize words, unless it is a product name, API, or other word that commonly is capatilized. 

| Do ✅ | Don't ❌ | 
| -- | -- | 
| Use the HTTPS protocol to send traffic. | Use the https protcol to send traffic. 
| Configure external authentication. | Configure External Authentication. | 

## Title case for titles

Use title case for the value of `title:` in the front matter of your markdown page. Title case capitalizes the first letter in any word. 

| Do ✅ | Don't ❌ | 
| -- | -- |
| Local rate limiting | Local Rate Limiting | 
| Shadowing | shadowing | 

## Simple, present tense

Use simple, present tense throughout the content that you want to add. Avoid past and future tense, unless it is required to convery the correct information. 

| Do ✅ | Don't ❌ | 
| -- | -- |
| Verify that the pod runs. | Verify that the pod is running. | 
| When you click this button, the UI opens. | When you click this button, the UI will open. | 
| To create the CORS policy, follow this example.  | In order to create the CORS policy, look at the example below and follow its instructions. | 

## Active voice

Make sure to use active voice where the subject of the sentence performs the action that is described by the verb. 

| Do ✅ | Don't ❌ | 
| -- | -- |
| You can enhance the security of your gateway with CORS policies. | Security of your gateway can be enhanced with CORS policies. | 
| During an update, the management plane cannot update Envoy filters. | During an update, there are Envoy filters that it can't update | 

## "I" and "we"

Avoid "I" and "we" in your content contribution. Instead, phrase sentences in the second-person or use the term user. 

| Do ✅ | Don't ❌ | 
| -- | -- |
| In this topic, set up traffic shadowing.| In this topic, we will set up a traffic shadowing. | 
| With kgateway, you can set up advanced traffic routing. | We offer advanced traffic routing.| 

## Future statements

Avoid making promises or giving hints about the future releases and features. If you want want to talk about a feature that is still under development, mark it as experimental or beta and use proper callout shortcodes to draw the user's attention to that information.

| Do ✅ | Don't ❌ | 
| -- | -- |
| `<omit this information, do not mention>` | We plan to deliver a new routing feature in the next release. | 
