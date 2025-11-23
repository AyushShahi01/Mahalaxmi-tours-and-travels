from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

from toures.models import Package
from system.models import Traveler, Ticket, Payment


class Command(BaseCommand):
    help = 'Populates the database with dummy data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Payment.objects.all().delete()
            Ticket.objects.all().delete()
            Traveler.objects.all().delete()
            Package.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared all data'))

        self.stdout.write(self.style.MIGRATE_HEADING('Creating dummy data...'))

        # Create Packages
        packages_data = [
            {
                'package_id': 'PKG001',
                'title': 'Everest Base Camp Trek',
                'description': 'Experience the ultimate Himalayan adventure with stunning views of Mount Everest and surrounding peaks. This 12-day trek takes you through Sherpa villages, ancient monasteries, and breathtaking landscapes.',
                'price': 1500,
                'duration': 12,
                'group_size': 15,
                'start_date': timezone.now().date() + timedelta(days=30),
                'cover_image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800',
                'tour_highlights': [
                    'Views of Mount Everest (8,848m)',
                    'Visit Namche Bazaar',
                    'Explore Tengboche Monastery',
                    'Experience Sherpa culture',
                    'Professional mountain guides'
                ],
                'tour_details': [
                    'Day 1: Fly to Lukla and trek to Phakding',
                    'Day 2-3: Trek to Namche Bazaar (3,440m)',
                    'Day 4: Acclimatization day',
                    'Day 5-6: Trek to Tengboche and Dingboche',
                    'Day 7-8: Reach Everest Base Camp',
                    'Day 9-12: Return trek to Lukla'
                ]
            },
            {
                'package_id': 'PKG002',
                'title': 'Annapurna Circuit Adventure',
                'description': 'Journey through diverse landscapes from subtropical forests to high mountain passes. This 14-day trek offers spectacular mountain views and cultural immersion.',
                'price': 1800,
                'duration': 14,
                'group_size': 12,
                'start_date': timezone.now().date() + timedelta(days=45),
                'cover_image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
                'tour_highlights': [
                    'Cross Thorong La Pass (5,416m)',
                    'Visit Muktinath Temple',
                    'Explore diverse ecosystems',
                    'Experience local hospitality',
                    'Panoramic Himalayan views'
                ],
                'tour_details': [
                    'Day 1-3: Trek from Besisahar to Chame',
                    'Day 4-6: Reach Manang for acclimatization',
                    'Day 7-8: Cross Thorong La Pass',
                    'Day 9-10: Descend to Jomsom',
                    'Day 11-14: Complete circuit via Tatopani'
                ]
            },
            {
                'package_id': 'PKG003',
                'title': 'Langtang Valley Trek',
                'description': 'Explore the beautiful Langtang Valley, known as the "Valley of Glaciers". This 8-day trek offers stunning mountain views and traditional Tamang culture.',
                'price': 950,
                'duration': 8,
                'group_size': 10,
                'start_date': timezone.now().date() + timedelta(days=20),
                'cover_image': 'https://images.unsplash.com/photo-1486870591958-9b9d0d1dda99?w=800',
                'tour_highlights': [
                    'Langtang National Park',
                    'Kyanjin Gompa Monastery',
                    'Tamang heritage villages',
                    'Glacier views',
                    'Wildlife spotting'
                ],
                'tour_details': [
                    'Day 1-2: Drive to Syabrubesi and trek to Lama Hotel',
                    'Day 3-4: Trek to Langtang Village and Kyanjin Gompa',
                    'Day 5: Acclimatization and exploration',
                    'Day 6-8: Return trek to Syabrubesi'
                ]
            },
            {
                'package_id': 'PKG004',
                'title': 'Chitwan Jungle Safari',
                'description': 'Wildlife adventure in Chitwan National Park, a UNESCO World Heritage Site. Spot rhinos, tigers, elephants, and exotic birds in their natural habitat.',
                'price': 600,
                'duration': 4,
                'group_size': 20,
                'start_date': timezone.now().date() + timedelta(days=15),
                'cover_image': 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800',
                'tour_highlights': [
                    'Jeep safari in the jungle',
                    'Canoe ride on Rapti River',
                    'Elephant breeding center visit',
                    'Bird watching tours',
                    'Tharu cultural dance'
                ],
                'tour_details': [
                    'Day 1: Arrival and jungle orientation',
                    'Day 2: Morning elephant safari, afternoon canoe ride',
                    'Day 3: Full day jeep safari',
                    'Day 4: Bird watching and departure'
                ]
            },
            {
                'package_id': 'PKG005',
                'title': 'Pokhara Paragliding Experience',
                'description': 'Soar like a bird over the beautiful Pokhara Valley with stunning views of Phewa Lake and the Annapurna range. Perfect for adventure seekers!',
                'price': 350,
                'duration': 1,
                'group_size': 5,
                'start_date': timezone.now().date() + timedelta(days=10),
                'cover_image': 'https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=800',
                'tour_highlights': [
                    'Tandem paragliding flight',
                    'Views of Phewa Lake',
                    'Annapurna mountain panorama',
                    'Experienced pilots',
                    'Photo and video package'
                ],
                'tour_details': [
                    'Day 1: Morning pickup from hotel',
                    'Drive to Sarangkot takeoff point',
                    '30-45 minute paragliding flight',
                    'Landing at lakeside',
                    'Certificate presentation'
                ]
            },
            {
                'package_id': 'PKG006',
                'title': 'Kathmandu Heritage Tour',
                'description': 'Explore the rich cultural heritage of Kathmandu Valley. Visit ancient temples, palaces, and UNESCO World Heritage Sites.',
                'price': 450,
                'duration': 4,
                'group_size': 25,
                'start_date': timezone.now().date() + timedelta(days=7),
                'cover_image': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800',
                'tour_highlights': [
                    'Visit 7 UNESCO World Heritage Sites',
                    'Explore Swayambhunath (Monkey Temple)',
                    'Tour Patan Durbar Square',
                    'Visit Pashupatinath Temple',
                    'Cultural guide and insights'
                ],
                'tour_details': [
                    'Day 1: Kathmandu Durbar Square, Swayambhunath',
                    'Day 2: Patan Durbar Square, Boudhanath Stupa',
                    'Day 3: Bhaktapur Durbar Square, Pashupatinath',
                    'Day 4: Shopping and local cuisine tour'
                ]
            }
        ]

        packages = []
        for pkg_data in packages_data:
            package = Package.objects.create(**pkg_data)
            packages.append(package)
            self.stdout.write(self.style.SUCCESS(f'✓ Created package: {package.title}'))

        # Create Travelers
        travelers_data = [
            {'name': 'Sarah Johnson', 'email': 'sarah.j@email.com', 'phone_number': '+1-555-0101', 'address': '123 Oak Street, New York, NY 10001, USA'},
            {'name': 'Michael Chen', 'email': 'mchen@email.com', 'phone_number': '+1-555-0102', 'address': '456 Pine Avenue, San Francisco, CA 94102, USA'},
            {'name': 'Emma Williams', 'email': 'emma.w@email.com', 'phone_number': '+44-20-7123-4567', 'address': '789 Baker Street, London, W1U 6TY, UK'},
            {'name': 'David Kumar', 'email': 'dkumar@email.com', 'phone_number': '+91-98765-43210', 'address': '321 MG Road, Bangalore, Karnataka 560001, India'},
            {'name': 'Sophie Martin', 'email': 'sophie.m@email.com', 'phone_number': '+33-1-42-34-56-78', 'address': '654 Rue de Rivoli, Paris, 75001, France'},
            {'name': 'James Anderson', 'email': 'j.anderson@email.com', 'phone_number': '+61-2-9876-5432', 'address': '987 George Street, Sydney, NSW 2000, Australia'},
            {'name': 'Maria Rodriguez', 'email': 'maria.r@email.com', 'phone_number': '+34-91-234-5678', 'address': '147 Gran Via, Madrid, 28013, Spain'},
            {'name': 'Robert Taylor', 'email': 'rtaylor@email.com', 'phone_number': '+1-555-0103', 'address': '258 Main Street, Toronto, ON M5H 2N2, Canada'},
            {'name': 'Lisa Schmidt', 'email': 'lisa.s@email.com', 'phone_number': '+49-30-1234-5678', 'address': '369 Unter den Linden, Berlin, 10117, Germany'},
            {'name': 'Yuki Tanaka', 'email': 'yuki.t@email.com', 'phone_number': '+81-3-1234-5678', 'address': '741 Shibuya, Tokyo, 150-0002, Japan'},
        ]

        travelers = []
        for traveler_data in travelers_data:
            traveler = Traveler.objects.create(**traveler_data)
            travelers.append(traveler)
            self.stdout.write(self.style.SUCCESS(f'✓ Created traveler: {traveler.name}'))

        # Create Tickets
        tickets = []
        for i, traveler in enumerate(travelers):
            # Each traveler books 1-2 packages
            num_bookings = random.randint(1, 2)
            selected_packages = random.sample(packages, num_bookings)
            
            for package in selected_packages:
                ticket = Ticket.objects.create(
                    package=package,
                    traveler=traveler
                )
                tickets.append(ticket)
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Created ticket #{ticket.ticket_id}: {traveler.name} → {package.title}'
                ))

        # Create Payments
        for ticket in tickets:
            # Create 1-3 payments per ticket (simulating installments)
            num_payments = random.randint(1, 3)
            total_price = Decimal(str(ticket.package.price))
            
            # Generate random payment amounts that sum to the total
            if num_payments == 1:
                amounts = [total_price]
            else:
                # Split into random proportions
                proportions = [random.random() for _ in range(num_payments)]
                total_proportion = sum(proportions)
                amounts = [total_price * Decimal(str(p / total_proportion)) for p in proportions]
                
                # Adjust last payment to match exact total
                amounts[-1] = total_price - sum(amounts[:-1])

            for j, amount in enumerate(amounts):
                payment = Payment.objects.create(
                    amount=round(amount, 2),
                    traveler=ticket.traveler,
                    ticket=ticket,
                    package=ticket.package
                )
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Created payment #{payment.payment_id}: ${payment.amount} for ticket #{ticket.ticket_id}'
                ))

        # Summary
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Packages created: {Package.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Travelers created: {Traveler.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Tickets created: {Ticket.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Payments created: {Payment.objects.count()}'))
        self.stdout.write(self.style.MIGRATE_HEADING('\n✓ Database population complete!'))
