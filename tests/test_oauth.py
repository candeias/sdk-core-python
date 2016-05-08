import unittest
from mastercard.security.oauth import OAuthAuthentication, OAuthParameters
from mastercard.core.config import Config
import mastercard.security.util as SecurityUtil
import mastercard.core.util as Util
import os


class OAuthTest(unittest.TestCase):

    def setUp(self):
        keyFile = os.path.dirname(os.path.realpath(__file__))+"/MCOpenAPI.p12"
        self.auth = OAuthAuthentication("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", keyFile, "mckp", "mcapi")
        Config.setAuthentication(self.auth)


    def test_getNonce(self):

        nonce = SecurityUtil.getNonce()
        self.assertEqual(len(nonce),16)

    def test_getTimestamp(self):

        timestamp = SecurityUtil.getTimestamp()
        self.assertEqual(len(str(timestamp)),10)


    def test_getBodyHash(self):

        body = '<?xml version="1.0" encoding="Windows-1252"?><ns2:TerminationInquiryRequest xmlns:ns2="http://mastercard.com/termination"><AcquirerId>1996</AcquirerId><TransactionReferenceNumber>1</TransactionReferenceNumber><Merchant><Name>TEST</Name><DoingBusinessAsName>TEST</DoingBusinessAsName><PhoneNumber>5555555555</PhoneNumber><NationalTaxId>1234567890</NationalTaxId><Address><Line1>5555 Test Lane</Line1><City>TEST</City><CountrySubdivision>XX</CountrySubdivision><PostalCode>12345</PostalCode><Country>USA</Country></Address><Principal><FirstName>John</FirstName><LastName>Smith</LastName><NationalId>1234567890</NationalId><PhoneNumber>5555555555</PhoneNumber><Address><Line1>5555 Test Lane</Line1><City>TEST</City><CountrySubdivision>XX</CountrySubdivision><PostalCode>12345</PostalCode><Country>USA</Country></Address><DriversLicense><Number>1234567890</Number><CountrySubdivision>XX</CountrySubdivision></DriversLicense></Principal></Merchant></ns2:TerminationInquiryRequest>'
        encodedHash = Util.base64Encode(Util.sha1Encode(body))
        self.assertEqual(encodedHash,"WhqqH+TU95VgZMItpdq78BWb4cE=")



    def test_getBaseString(self):

        body = '<?xml version="1.0" encoding="Windows-1252"?><ns2:TerminationInquiryRequest xmlns:ns2="http://mastercard.com/termination"><AcquirerId>1996</AcquirerId><TransactionReferenceNumber>1</TransactionReferenceNumber><Merchant><Name>TEST</Name><DoingBusinessAsName>TEST</DoingBusinessAsName><PhoneNumber>5555555555</PhoneNumber><NationalTaxId>1234567890</NationalTaxId><Address><Line1>5555 Test Lane</Line1><City>TEST</City><CountrySubdivision>XX</CountrySubdivision><PostalCode>12345</PostalCode><Country>USA</Country></Address><Principal><FirstName>John</FirstName><LastName>Smith</LastName><NationalId>1234567890</NationalId><PhoneNumber>5555555555</PhoneNumber><Address><Line1>5555 Test Lane</Line1><City>TEST</City><CountrySubdivision>XX</CountrySubdivision><PostalCode>12345</PostalCode><Country>USA</Country></Address><DriversLicense><Number>1234567890</Number><CountrySubdivision>XX</CountrySubdivision></DriversLicense></Principal></Merchant></ns2:TerminationInquiryRequest>'
        method = "POST"
        url = "https://sandbox.api.mastercard.com/fraud/merchant/v1/termination-inquiry?Format=XML&PageLength=10&PageOffset=0"

        oAuthParameters = OAuthParameters()
        oAuthParameters.setOAuthConsumerKey("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        oAuthParameters.setOAuthNonce("1111111111111111111")
        oAuthParameters.setOAuthTimestamp("1111111111")
        oAuthParameters.setOAuthSignatureMethod("RSA-SHA1")
        oAuthParameters.setOAuthVersion("1.0")
        encodedHash = Util.base64Encode(Util.sha1Encode(body))

        oAuthParameters.setOAuthBodyHash(encodedHash)

        baseString = OAuthAuthentication.getBaseString(url, method, oAuthParameters.getBaseParametersDict());
        self.assertEqual(baseString,'POST&https%3A%2F%2Fsandbox.api.mastercard.com%2Ffraud%2Fmerchant%2Fv1%2Ftermination-inquiry&Format%3DXML%26PageLength%3D10%26PageOffset%3D0%26oauth_body_hash%3DWhqqH%252BTU95VgZMItpdq78BWb4cE%253D%26oauth_consumer_key%3Dxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx%26oauth_nonce%3D1111111111111111111%26oauth_signature_method%3DRSA-SHA1%26oauth_timestamp%3D1111111111%26oauth_version%3D1.0')


    def test_signMessage(self):

        baseString = 'POST&https%3A%2F%2Fsandbox.api.mastercard.com%2Ffraud%2Fmerchant%2Fv1%2Ftermination-inquiry&Format%3DXML%26PageLength%3D10%26PageOffset%3D0%26oauth_body_hash%3DWhqqH%252BTU95VgZMItpdq78BWb4cE%253D%26oauth_consumer_key%3Dxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx%26oauth_nonce%3D1111111111111111111%26oauth_signature_method%3DRSA-SHA1%26oauth_timestamp%3D1111111111%26oauth_version%3D1.0'

        signature = self.auth.signMessage(baseString)
        signature = Util.uriRfc3986Encode(signature)

        self.assertEqual(signature,"Yh7m15oV0XbRTFP%2Fp4T56sg38QDLKEh4cVK90taaHstE%2FjTdCn53CtbUETQFWLR2VdMMv8ujeewM3NDzLRfVLqwE%2FsWbpeaWtm%2FpffAvHjXFTquo4hBE6CPRNEqFyIjCz4lNaYoeaQMFJVmYfSF2CWn46RP3wmIrfs5IfQNtwUI%3D")




if __name__ == '__main__':
    unittest.main()