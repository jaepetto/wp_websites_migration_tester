import uuid
import os
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from jinja2 import Template, Environment, PackageLoader, select_autoescape
from compared_page import ComparedPage
from skimage.measure import compare_ssim
import argparse
import imutils
import cv2
import numpy as np


def test_site(driver: webdriver, image_path: str, url: str, username: str, password: str) -> str:
    driver.get(url)

    # Checks if the coming soon title is present
    try:
        coming_soon_title = driver.find_element_by_xpath('//*[@id="seed-csp4-headline"]')
        login_link = driver.find_element_by_xpath("//a[starts-with(@href, 'wp-admin/')]")
        login_link.click()
        username_field = driver.find_element_by_xpath("//*[@id='user_login']")
        username_field.clear()
        username_field.send_keys(username)
        password_field = driver.find_element_by_xpath("//*[@id='user_pass']")
        password_field.clear()
        password_field.send_keys(password)
        submit_button = driver.find_element_by_xpath("//*[@id='wp-submit']")
        submit_button.click()
    except NoSuchElementException:
        pass

    driver.get(url)

    try:
        consent_button = driver.find_element_by_xpath("//a[starts-with(@aria-label, 'dismiss cookie message')]")
        executor = driver
        executor.execute_script("arguments[0].click();", consent_button)
    except NoSuchElementException:
        pass

    id = uuid.uuid4()
    filename = "{}.png".format(id)
    filepath = "{}/{}".format(images_path, filename)

    driver.get_screenshot_as_file(filepath)

    return filename


if __name__ == "__main__":

    # base config for running the tests
    sessionid = str(uuid.uuid4())
    reportpath = "out/{}".format(sessionid)
    if not os.path.exists(reportpath):
        os.makedirs(reportpath)
    images_path = "{}/img".format(reportpath)
    if not os.path.exists(images_path):
        os.makedirs(images_path)

    result = []

    driver = webdriver.Firefox()
    driver.set_window_size(1024, 768)

    datas = pd.read_csv('lot1_login_infos.csv')

    for index, row in datas.iterrows():
        current_result = ComparedPage()

        current_result.WP_url = row['url']
        current_result.WP_username = row['login']
        current_result.WP_password = row['password']
        current_result.WP_screenshot_file = test_site(driver, images_path, row['url'], row['login'], row['password'])

        current_result.Jahia_url = row['jahia_url']
        current_result.Jahia_screenshot_file = test_site(driver, images_path, row['jahia_url'], current_result.Jahia_username, current_result.Jahia_password)

        imageA = cv2.imread("{}/{}".format(images_path, current_result.Jahia_screenshot_file))
        imageB = cv2.imread("{}/{}".format(images_path, current_result.WP_screenshot_file))

        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        (score, diff) = compare_ssim(grayA, grayB, full=True)
        current_result.SSIM_score = score


        # threshold the difference image, followed by finding contours to
        # obtain the regions of the two input images that differ

        #thresh = cv2.threshold(np.float32(diff.copy()), 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        #thresh = cv2.threshold(np.float32(diff.copy()), 0, 255, cv2.THRESH_BINARY_INV)[1]


        #cnts = cv2.findContours(np.uint8(thresh.copy()), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #cnts = cnts[0] if imutils.is_cv2() else cnts[1]

        # loop over the contours
        # for c in cnts:
        #     # compute the bounding box of the contour and then draw the
        #     # bounding box on both input images to represent where the two
        #     # images differ
        #     (x, y, w, h) = cv2.boundingRect(c)
        #     cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
        #     cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # show the output images
        #cv2.imshow("Original", imageA)
        #cv2.imshow("Modified", imageB)
        #cv2.imshow("Diff", diff)
        #cv2.imshow("Thresh", thresh)
        #cv2.waitKey(0)

        for person in str(row['responsable']).split('|'):
            current_result.Persons_in_charge.append(person.strip())

        result.append(current_result)
    driver.close()

    average_score = sum(current_result.SSIM_score for current_result in result) / float(len(result))

    # time for reporting
    # jinja2 environment
    env = Environment(
        loader=PackageLoader('wp_websites_migration_tester', 'templates'),
        autoescape=select_autoescape('html', 'xml'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template('report.html')

    report = template.render(sites=result)

    reportfilepath = "{}/report.html".format(reportpath)
    with open(reportfilepath, "w") as fh:
        fh.write(report)

