#include <opencv2/imgproc/imgproc_c.h>
#include <opencv2/highgui/highgui.hpp>
#include <stdio.h>

int main( int argc, char** argv ){
	CvMemStorage* storage = cvCreateMemStorage(0);
	CvSeq* contour = 0;
	IplImage *img = cvLoadImage(argv[1], CV_LOAD_IMAGE_GRAYSCALE);
	cvFindContours( img, storage, &contour, sizeof(CvContour),
		CV_RETR_TREE, CV_CHAIN_APPROX_SIMPLE, cvPoint(0,0) );
	CvTreeNodeIterator iterator;
	cvInitTreeNodeIterator( &iterator, contour, 9 );
	while( (contour = (CvSeq*)cvNextTreeNode( &iterator )) != 0 ){
		int hole = contour->flags & CV_SEQ_FLAG_HOLE; 
		//printf("%i, %f\n", hole, cvContourArea(contour, CV_WHOLE_SEQ, 0));
		printf("%i,", hole);
	}
	printf("\n");
    fflush(stdout);
	return 0;
}
