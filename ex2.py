from pathlib import Path
import argparse
import sys
import logging
import cv2
from numpy import ndarray, uint8, zeros

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)


IMG0_NAME='./datasets/hill-ir-rot-0007.png'
IMG1_NAME='./datasets/hill-rgb-0007.png'


class IMGOP():
    ''' Image Operation Class '''
    def __init__(self, fpath):
        self.fpath = Path(fpath)
        self.name = self.fpath.name
        self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0
        self.img = ndarray([], dtype=uint8)
        self.roi = ndarray([], dtype=uint8)
        self.cropped = False
        self.logger = logging.getLogger('IMGOP')

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.x0, self.y0 = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            self.x1, self.y1 = x+1, y+1
            # comppensate for quick click
            if self.x1 == self.x0:
                self.x1 += 1
            if self.y1 == self.y0:
                self.y1 += 1
 
            self.cropped = True
            self.logger.debug(f'{self.x0}, {self.y0}, {self.x1}, {self.y1}')

    def crop(self):
        ''' Sets the roi from specified values
            was separated to be able to be used in a unittest
        '''
        self.roi = self.img[self.y0:self.y1, self.x0:self.x1]

    def run(self):
        ''' 
            Shows the image, waits for the user to select
            an area then sets the ROI array
        '''
        self.read_img()
        cv2.imshow(self.name, self.img)
        cv2.namedWindow(self.name)
        cv2.setMouseCallback(self.name, self.mouse_callback)

        while not self.cropped:
            cv2.waitKey(10);

        cv2.destroyWindow(self.name)
        self.crop()
        
    def write_roi(self):
        '''
            Writes the Region of interest to disk with a suffix roi
        '''
        result_name = str(self.fpath.parent.absolute()) \
                + '/' \
                + str(self.fpath.stem) \
                + "-roi" \
                + str(self.fpath.suffix)

        status = cv2.imwrite(result_name, self.roi)
        self.logger.debug(f'{result_name} written?: {status}')

    def show_roi(self, delay):
        '''
            Displays the Region of interest in a window
        '''
        cv2.imshow(self.name+"-roi", self.roi)
        cv2.waitKey(delay)
        cv2.destroyWindow(self.name+"-roi")

    def read_img(self):
        '''
            Reads the image specified at init
            @throws a Value Error if file doesnt exist
        '''
        if not self.fpath.exists():
            raise ValueError("error: filepath doesn't exist")
        self.img = cv2.imread(str(self.fpath), cv2.IMREAD_COLOR)

    def write_img(self):
        '''
            Writes the image to disk
            This is used for a the result image
        '''
        status = cv2.imwrite(str(self.fpath), self.img)
        self.logger.debug(f'{self.name} written?: {status}')
    
    def show_img(self, delay):
        '''
            Displays self.img in a window
        '''
        cv2.imshow(self.name, self.img)
        cv2.waitKey(delay)
        cv2.destroyWindow(self.name)

    def __repr__(self):
        return (self.name, self.fpath)

    def __add__(self, other):
        ''' 
            Returns the concatenated ROI of 2 IMGOPs
        '''
        result_name = str(self.fpath.parent.absolute()) \
                + '/' \
                + str(self.fpath.stem) \
                + "-aligned" \
                + str(self.fpath.suffix)
        new = IMGOP(result_name)
        new.y0, new.x0 = self.roi.shape[:2]
        new.y1, new.x1 = other.roi.shape[:2]
        new.img = zeros((max(new.y0, new.y1), new.x0+new.x1, 3), uint8)
        new.img[:new.y0, :new.x0,:3] = self.roi
        new.img[:new.y1, new.x0:new.x0+new.x1,:3] = other.roi
        return new

    def feature_match(self, other):
        '''
            Applies homography on the zones
        '''

        # Initiate SIFT detector
        sift = cv2.SIFT_create()

        # find the keypoints and descriptors with SIFT

        img1 = cv2.cvtColor(self.roi, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(other.roi, cv2.COLOR_BGR2GRAY)

        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2,None)

        # FLANN parameters
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)   # or pass empty dictionary
        flann = cv2.FlannBasedMatcher(index_params,search_params)
        matches = flann.knnMatch(des1,des2,k=2)
        # Need to draw only good matches, so create a mask
        matchesMask = [[0,0] for i in range(len(matches))]
        # ratio test as per Lowe's paper
        for i,(m,n) in enumerate(matches):
            if m.distance < 0.7*n.distance:
                matchesMask[i]=[1,0]
        draw_params = dict(matchColor = (0,255,0),
                           singlePointColor = (255,0,0),
                           matchesMask = matchesMask,
                           flags = cv2.DrawMatchesFlags_DEFAULT)
        img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, matches, None, **draw_params)

        return img3


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("img0", default=IMG0_NAME, help="path for the first image")
    parser.add_argument("img1", default=IMG1_NAME, help="path for the second image")
    args = parser.parse_args()
    # create the image operational handlers
    hill0= IMGOP(args.img0)
    hill1= IMGOP(args.img1)
    # get user input to crop images in their ROIj
    hill0.run()
    hill1.run()
    # concat the ROI and conviently create a new image object
    concat = hill0 + hill1
    # write the image back to disk
    concat.write_img()
    #concat.show_img(1500)
    img3 = hill0.feature_match(hill1)
    cv2.imshow('feature_match', img3)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
    sys.exit(0)


